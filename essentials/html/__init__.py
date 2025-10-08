
def createTable(data, req=False):
    if req == False:
        html = "<table style='width: 100%'>\n\t<tbody>\n"
    else:
        html = ""
    for key in data:
        if type(data[key]) == dict:
            html += createTable(data[key], True)
        else:
            html += f"\t<tr>\n\t\t<td>{key}</td>\n\t<td>\n\t\t<input placeholder='' name='{key}' id='{key}'>\n\t</td>\n\t</tr>\n"
    if req == False:
        html += "\t</tbody>\n</table>"
    return html