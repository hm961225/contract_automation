import json
import os
import uuid

from flask import Blueprint, render_template, request, redirect, url_for, session

from app.utils.xml_analyze import WorkflowHandle
from app.utils.file_option import file_save, read_new_file
from app.models.smart_contract import SmartContract, OriginFunction
from app.models import db_session


contract_add_bp = Blueprint("contract_add_bp", __name__)
func_data = None
FUNCTION_SAVE_PATH = "./static/bpmn_file/"
CONTRACT_SAVE_PATH = "./static/smart_contract_file/"

@contract_add_bp.route("/add_contract", methods=['GET', 'POST'])
def add_contract():
    """
    接收前端textarea元素的全部文本，将该文本保存为.go智能合约文件
    :return:
    """
    smart_contract_name_list = []
    func_name = request.args.get("func_name")
    global func_data
    smart_contract_obj_list = OriginFunction.query.all()

    for one_obj in smart_contract_obj_list:
        smart_contract_name_list.append(one_obj.origin_name)

    if func_name:
        if func_data:
            new_data = read_new_file(os.getcwd() + "/static/bpmn_file/" + func_name + ".go")
            func_data += "\n" "\n" + new_data
        else:
            func_data = read_new_file(os.getcwd() + "/static/bpmn_file/" + func_name + ".go")

    if request.method == "POST":
        contract_text = request.form.get("contract_text")
        if contract_text:
            file_uuid_name = uuid.uuid4()
            smart_contract_name = request.form.get("contract_name")
            file_save(CONTRACT_SAVE_PATH, smart_contract_name, "go", contract_text)
            # 数据入库
            new_record = SmartContract(origin_name=smart_contract_name,
                                        code_file_name=file_uuid_name)
            db_session.add(new_record)
            db_session.commit()
            func_data = None
        # func_data = request.values.get("func_data")

    return render_template("add_contract.html",
                           func_data=func_data,
                           smart_contract_name_list=smart_contract_name_list
                           )

@contract_add_bp.route("/function_add", methods=['GET', 'POST'])
def function_add():
    if request.method == "POST":
        json_data = request.get_data()
        data = json.loads(json_data)
        content = data["data"]
        origin_name = data["name"]

        bpmn_file_uuid_name = uuid.uuid4()
        file_save(FUNCTION_SAVE_PATH, origin_name, "bpmn", content)

        xml_analyze_obj = WorkflowHandle(f"{FUNCTION_SAVE_PATH}{origin_name}.bpmn")
        go_code_text, go_file_uuid_name = xml_analyze_obj.run()
        file_save(FUNCTION_SAVE_PATH, origin_name, "go", go_code_text)
        # 数据入库
        new_record = OriginFunction(origin_name=origin_name,
                                   bpmn_file_name=bpmn_file_uuid_name,
                                   code_file_name=go_file_uuid_name)
        db_session.add(new_record)
        db_session.commit()
        print(f"origin_name:{origin_name},"
              f" bpmn_file_name:{bpmn_file_uuid_name},"
              f" code_file_name:{go_file_uuid_name}"
              f" insert successfully")

    return ""

@contract_add_bp.route("/function_show", methods=['GET', 'POST'])
def function_show():
    # 可以通过接口的方式来实现数据显示
    func_name = request.args.get("func_name")
    print(f"func_name: {func_name}")

    return redirect(url_for("contract_add_bp.add_contract", func_name=func_name))

@contract_add_bp.route("/xml_extract/<xml_file_name>", methods=['GET', 'POST'])
def xml_extract(xml_file_name):
    if request.method == "POST":
        xml_analyze_obj = WorkflowHandle(xml_file_name)
        res_text, res_file_name = xml_analyze_obj.run()

@contract_add_bp.route("/remove_func_data", methods=['GET', 'POST'])
def remove_func_data():
    global func_data
    func_data = None

    return redirect(url_for("contract_add_bp.add_contract"))

@contract_add_bp.route("/api_test", methods=['GET', 'POST'])
def api_test():
    if request.method == "POST":
        json_data = request.get_data()
        data = json.loads(json_data)
        with open("./static/bpmn_file/test.txt", "w") as f:
            f.write(data["data"])
        print(data["name"])
    return ""