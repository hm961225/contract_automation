from flask import Blueprint, render_template, request, redirect, url_for, session

from app.utils.make_new_file import make_new_file, read_new_file
import os


contract_add_bp = Blueprint("contract_add_bp", __name__)
func_data = None

@contract_add_bp.route("/add_contract", methods=['GET', 'POST'])
def add_contract():
    """
    接收前端textarea元素的全部文本，将该文本保存为.go智能合约文件
    :return:
    """
    func_name = request.args.get("func_name")
    global func_data

    if func_name:
        if func_data:
            new_data = read_new_file(os.getcwd() + "/data/" + func_name + ".go")
            func_data += "\n" "\n" + new_data
            print(func_data)
        else:
            func_data = read_new_file(os.getcwd() + "/data/" + func_name + ".go")

    if request.method == 'POST':
        contract_text = request.form.get("contract_text")
        if contract_text:
            # contract_name = request.form.get("contract_name")
            contract_name = "test_file"
            make_new_file(contract_name, contract_text)
        # func_data = request.values.get("func_data")


    return render_template("add_contract.html", func_data=func_data)

@contract_add_bp.route("/function_show", methods=['GET', 'POST'])
def function_show():
    # 可以通过接口的方式来实现数据显示
    func_name = request.args.get("func_name")

    return redirect(url_for("contract_add_bp.add_contract", func_name=func_name))