import xml.dom.minidom as xmldom
import uuid


class WorkflowHandle(object):
    '''
    思路：
    1. 先用一个dict保存所有task以及gateway的顺序。
    2. 同时用一个dict来保存task_id及name(task内容)
    3. 顺序从list中取任务，如果是task则直接执行(即读取内容写入代码文件中)，如果是gateway或者循环任务，则写函数来进行处理
    4. 具体的处理方法：读取gateway中的全部outgoing标签（如果有yes和no则说明有两个操作，可能需要加else）。其中outgoing中存的是线条id
       所以需要根据这个id去读取线条是否有Yes和No的字样。如果有再读取该线条中的targetRef标签得到其指向的task_id，再去字典中取内容。此
       时还要注意，需要把该task_id在dict中标记已经被访问过，避免重复运行。
    5. 循环标签只有Yes
    '''
    IGNORE_NODE_NAME = ("StartEvent", "SequenceFlow", "EndEvent", "ExclusiveGateway", "ComplexGateway")
    INDENT = "    "
    CUR_INDENT = ""  # 处理if和for的缩进问题
    SPECIAL_HANDLE_LIST = ("Gateway", "InclusiveGateway")
    END_TASK_TYPE = {"Gateway": "ExclusiveGateway",
                     "InclusiveGateway": "ComplexGateway"
                     }

    def __init__(self, file_path):
        self.doc = xmldom.parse(file_path)
        self.process = self.doc.documentElement.getElementsByTagName("process")[0]
        self.flow_list = self.process.getElementsByTagName("sequenceFlow")
        self.task_order_list = {}  # 保存task顺序，value为Ture表示被访问过
        self.task_dict = {}  # 保存task_id和task_content映射的字典
        self.text = ""
        self.save_file_name = ""  # 解析完成的txt文件存储位置

    def get_task_order(self):
        process = self.process
        task_index = 0
        gateway_index = 0
        inclusive_gateway_index = 0

        for child in process.childNodes:
            try:
                # 获取各个节点的类型（task或者其他）
                child_id = child.getAttribute("id")
                child_content = child.getAttribute("name")
                child_name = child_id.split("_")[0]
                self.task_dict[child_id] = child_content
                if child_name in self.IGNORE_NODE_NAME:
                    # 只需要记录判断、task、循环的顺序
                    continue
                child_name = child_name.lower()  # 统一转化为小写字母
                if child_name == "task":
                    child_name += "-" + str(task_index)
                    task_index += 1
                if child_name == "gateway":
                    child_name += "-" + str(gateway_index)
                    gateway_index += 1
                if child_name == "inclusivegateway":
                    child_name += "-" + str(inclusive_gateway_index)
                    inclusive_gateway_index += 1
                child_name += "-" + child_id
                self.task_order_list[child_name] = False
            except Exception:
                continue

    def handle_by_order(self):
        self.get_task_order()
        self.generate_func_head()

        for value in self.task_order_list:
            if self.task_order_list[value] == True:
                continue
            self.task_order_list[value] = True
            task_type, task_index, task_id = value.split("-")
            node = self.find_node_by_id(task_id)
            node_content = self.task_dict[task_id]
            if "exclusivegateway" in value:
                task_id, task_type = self.find_next_task_id_A_type_by_pre_id(task_id)
                node = self.find_node_by_id(task_id)
                node_content = self.task_dict[task_id]
                self.judge_used_by_id(task_id)
            if task_type == "gateway":
                self.text += self.CUR_INDENT + node_content + " {"
                self.text += '\n'
                self.handle_gateway(node, node_content, "Gateway", self.END_TASK_TYPE["Gateway"])
            elif task_type == "inclusivegateway":
                self.text += self.CUR_INDENT + node_content + " {"
                self.text += '\n'
                self.handle_gateway(node, node_content, "InclusiveGateway", self.END_TASK_TYPE["InclusiveGateway"])
            else:
                self.text += self.CUR_INDENT + node_content
                self.text += '\n'
        self.text += "}"  # 添加函数结尾的括号

    def handle_gateway(self, node, node_content, begin_task_type, end_task_type):
        if node_content == "":
            return
        self.CUR_INDENT += self.INDENT
        gateway_id = node.getAttribute("id")
        yes_flow_id, no_flow_id = "", ""
        flow_id_list = self.find_flow_source_ref(gateway_id)  # 一个是Yes flow_id，一个是No flow_id

        for id in flow_id_list:
            content = self.task_dict[id]
            if content == "Yes" or content == "yes":
                yes_flow_id = id
            elif content == "No" or content == "no":
                no_flow_id = id

        yes_flow_task, no_flow_task = self.find_flow_target_ref(yes_flow_id), self.find_flow_target_ref(no_flow_id)
        self.find_all_flow_content(yes_flow_task, begin_task_type, end_task_type)
        self.CUR_INDENT = self.CUR_INDENT[:-4]
        self.text += self.CUR_INDENT + "}"
        if no_flow_task:
            self.text += "else {" + "\n"
            self.CUR_INDENT += self.INDENT
            self.find_all_flow_content(no_flow_task, begin_task_type, end_task_type)
            self.CUR_INDENT = self.CUR_INDENT[:-4]
            self.text += self.CUR_INDENT + "}" + "\n"
        else:
            self.text += "\n"

    def find_all_flow_content(self, begin_task_node, begin_task_type, end_task_type):
        # 递归找，每找到一个task需要从order列表中将这个task去除
        if begin_task_node == None:
            return

        id = begin_task_node.getAttribute("id")
        if self.judge_used_by_id(id):
            return
        if self.task_dict[id] == "":
            return
        task_type, _ = id.split("_")
        if task_type not in self.SPECIAL_HANDLE_LIST:
            self.text += self.CUR_INDENT + self.task_dict[id]
            self.text += "\n"
        else:
            self.text += self.CUR_INDENT + self.task_dict[id] + " {" + "\n"
            self.handle_gateway(begin_task_node, self.task_dict[id], begin_task_type, self.END_TASK_TYPE[begin_task_type])

        next_task_id, next_task_type = self.find_next_task_id_A_type_by_pre_id(id)
        if next_task_type == end_task_type:
            return
        else:
            next_task = self.find_node_by_id(next_task_id)
        self.find_all_flow_content(next_task, begin_task_type, end_task_type)

    def find_node_by_id(self, id):
        for child in self.process.childNodes:
            try:
                # 获取各个节点的类型（task或者其他）
                child_id = child.getAttribute("id")
                if child_id == id:
                    return child
            except Exception:
                continue

    def find_flow_source_ref(self, flow_id):
        # 通过gateway_id获取到其出口的两个flow_id（yes和no的两个flow）
        res_list = []
        for flow in self.flow_list:
            source_id = flow.getAttribute("sourceRef")
            if source_id == flow_id:
                id = flow.getAttribute("id")
                res_list.append(id)
        return res_list

    def find_flow_target_ref(self, flow_id):
        for flow in self.flow_list:
            id = flow.getAttribute("id")
            if id == flow_id:
                target_id = flow.getAttribute("targetRef")
                target_node = self.find_node_by_id(target_id)
                return target_node

    def find_next_task_id_A_type_by_pre_id(self, pre_task_id):
        for child in self.process.childNodes:
            try:
                # 获取各个节点的类型（task或者其他）
                child_id = child.getAttribute("sourceRef")
                if child_id == pre_task_id:
                    return child.getAttribute("targetRef"), child.getAttribute("targetRef").split("_")[0]
            except Exception:
                continue
        return "", ""

    def judge_used_by_id(self, id):
        for value in self.task_order_list:
            if id in value and self.task_order_list[value] == False:
                self.task_order_list[value] = True
                return False
        return True

    def generate_func_head(self):
        function_name = self.process.getElementsByTagName("startEvent")[0].getAttribute("name")
        self.text += f"func {function_name}()" + " {" + "\n"
        self.CUR_INDENT += self.INDENT

    def generate_code_file(self):
        save_path = "/Users/heming/爬虫/xml_learn/"
        file_name = str(uuid.uuid4())
        full_path = save_path + file_name
        with open(full_path, "w") as f:
            f.write(self.text)

        self.save_file_name = file_name

    def run(self):
        self.handle_by_order()
        self.generate_code_file()

        return self.text, self.save_file_name