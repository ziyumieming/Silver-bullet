# start_url = f'https://www.kuaidaili.com/free/fps/1/'
# print('Crawling', start_url)
# html = get_page(start_url)

import execjs

# 提取的 JavaScript 代码（移除 document 相关操作）
js_code = """
function a(a){function n(){for(var a={wQzOV:"cookie",iTyzs:function(a,n){return a+n}},n=a["wQzOV"].split("|"),e=0;;){switch(n[e++]){case"0":t+="EO_Bot_Ssid=";continue;case"1":return t;case"2":t+="";continue;case"3":t=a["iTyzs"](t,1175126016);continue;case"4":var t="";continue}break}}var e={WTKkN:46999455,bOYDu:504387329,dtzqS:function(a,n){return a+n},wyeCN:289342924,pCQRM:function(a){return a()}},t=0;return t+=e["WTKkN"],t+=e["bOYDu"],t=e["dtzqS"](t,e["wyeCN"]),[t,e["pCQRM"](n)][a]}
"""

# 编译 JavaScript 代码
ctx = execjs.compile(js_code)

# 调用 JavaScript 函数
result = ctx.call("a", 0)  # 调用函数 a(0)
print("生成的值:", result)