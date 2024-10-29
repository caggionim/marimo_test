import marimo

__generated_with = "0.9.10-dev11"
app = marimo.App(width="medium", app_title="rheology_flowcurvefit")


@app.cell
def __():
    # import lmfit
    import pandas as pd
    import matplotlib.pyplot as plt
    from pathlib import Path
    import io
    import xlrd
    import pybroom
    import openpyxl
    import math
    from models import lmfit, model_dict
    return (
        Path,
        io,
        lmfit,
        math,
        model_dict,
        openpyxl,
        pd,
        plt,
        pybroom,
        xlrd,
    )


@app.cell
async def __():
    import micropip

    await micropip.install("latexify-py")
    import latexify
    return latexify, micropip


@app.cell
def __():
    import marimo as mo

    mo.md("""# Rheology flow curve analsys""")
    return (mo,)


@app.cell
def __(mo):
    select_file = mo.ui.file(label="upload file")
    mo.md(
        f"""## Upload data

    Upload file for analysis: {select_file}

    """
    )
    return (select_file,)


@app.cell
def __(io, mo, pd, select_file):
    mo.stop(select_file.contents() is None)

    data_file = pd.ExcelFile(io.BytesIO(select_file.contents()), engine="xlrd")

    step_list = data_file.sheet_names
    select_step = mo.ui.dropdown(options=step_list)
    mo.md(
        f"""## Select measurement step

    Select procedure step for analysis: {select_step}

    """
    )
    return data_file, select_step, step_list


@app.cell
def __(mo, model_dict):
    select_model = mo.ui.dropdown(options=model_dict)
    weight_model = mo.ui.radio(options=["absolute", "relative"], value="relative")

    mo.md(
        f"""## Select Model

    Select model: {select_model}

    Select residual weight: {weight_model}

    """
    )
    return select_model, weight_model


@app.cell
def __(latexify, mo, select_model):
    mo.stop(select_model.value == None)

    mo.md(
        f"""## Model Expression

    ${latexify.get_latex(select_model.value.func)}$"""
    )
    return


@app.cell
def __(mo, select_model):
    from rheo_widgets import make_ui_parameters, make_parameters_from_ui

    mo.stop(select_model.value is None)
    get_state, set_state = mo.state(None)


    ui_parameter = make_ui_parameters(select_model.value.make_params())
    ui_parameter.hstack()
    return (
        get_state,
        make_parameters_from_ui,
        make_ui_parameters,
        set_state,
        ui_parameter,
    )


@app.cell
def __(mo):
    min_shear_rate = mo.ui.text(label="minimum shear rate", value=str(0.01))
    max_shear_rate = mo.ui.text(label="max shear rate", value=str(10000))

    mo.vstack([min_shear_rate, max_shear_rate])
    return max_shear_rate, min_shear_rate


@app.cell
def __(
    data_file,
    make_parameters_from_ui,
    max_shear_rate,
    min_shear_rate,
    mo,
    select_file,
    select_model,
    select_step,
    ui_parameter,
    weight_model,
):
    from models import plot_fit_res

    mo.stop(select_file.value is None)
    mo.stop(select_model.value is None)

    model = select_model.value
    FC = data_file.parse(sheet_name=select_step.value, skiprows=[0, 2])
    params = make_parameters_from_ui(model, ui_parameter)

    condition = (FC["Shear rate"] > float(min_shear_rate.value)) & (
        FC["Shear rate"] < float(max_shear_rate.value)
    )
    if weight_model.value == "relative":
        weight = condition / FC["Shear rate"]
    elif weight_model.value == "absolute":
        weight = condition


    res = model.fit(
        FC["Stress"], x=FC["Shear rate"], weights=weight, params=params
    )
    mo.md(
        f"""{mo.as_html(plot_fit_res(res, min_shear_rate=min_shear_rate.value, max_shear_rate=max_shear_rate.value))}

    {mo.as_html(res)}
    """
    )
    return FC, condition, model, params, plot_fit_res, res, weight


@app.cell
def __():
    return


if __name__ == "__main__":
    app.run()
