'''
lua的自动完成插件

版权所有，未经允许不得用于商业用途
@homepage http://github.com/iamfredng/sublimehydra

@author fred(iamfredng@gmail.com)
'''

import sublime, sublime_plugin
import os.path, re, os, json, codecs

localvar_re = re.compile(r"\b(function\s+([a-zA-Z_.:]+[.:])?([a-zA-Z_]\w*)\s*\(([^)]*)\))")

class HydraLuaCompletionEventListener(sublime_plugin.EventListener):

    def __init__(self):
        self.scopeStack = []

    @staticmethod
    def getScopeName(self, view):
        """
        获取当前语法类型
        """
        return str(os.path.splitext(view.scope_name(1))[1]).strip()

    def processFile(self, folder):

        luaScriptFiles = os.listdir(folder)
        for x in luaScriptFiles:
            filePath = os.path.join(folder, x);
            if os.path.isdir(filePath):
                self.processFile(filePath)
            else:
                if str(os.path.splitext(x)[1]).strip() != ".lua":
                    continue
                print("processing file %s" %(filePath))
                f = codecs.open(filePath, "r", "utf-8")
                content = f.read()
                f.close()

                content = localvar_re.findall(content)

                for subContent in content:
#                    self.scopeStack.append([subContent[1] + subContent[2] + "\t" + subContent[0].replace("function", ""), subContent[1] + subContent[2] + "($1)$0"])
                    self.scopeStack.append([subContent[1].replace(".", "_").replace(":", "_") + subContent[2] + "\t" + subContent[0].replace("function", "") + " -luaP", subContent[1] + subContent[2] + "($1)$0"])

    def on_post_save(self, view):
        """
        当文件保存后执行重建索引操作
        """

        # 过滤掉不必的操作
        if view.settings().get("syntax") != "Packages/Lua/Lua.tmLanguage":
            return

        if not view.window().project_file_name():
            return

        luaFile=view.window().project_file_name()

        self.scopeStack.clear()

        luaScriptFolder = os.path.dirname(luaFile)
        self.processFile(luaScriptFolder)

        return None

    def on_query_completions(self, view, prefix, locations):
        # 过滤掉不必的操作
        if view.settings().get("syntax") != "Packages/Lua/Lua.tmLanguage":
            return
        return self.scopeStack