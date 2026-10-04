#!/usr/bin/env python3
"""Generate canonical Draw.io (.drawio), SVG, and spec.json diagram assets
for GCP Billing Account, Network Threats, and Identity/Authentication architectures.
Strictly adheres to Abstract Security design system:
Palette:
  - Dark canvas: #060608 / #04060c
  - Abstract Pink / Magenta: #FF216B, #E8005D, #C2004C
  - Abstract Teal: #01E69D
  - GCP Blue: #2E9BF0 / #4285F4
  - Warning / Alert Amber: #F5C61E
  - Wire / Line: #7D7589 / #2a2d35
Typography:
  - Barlow, Barlow Semi Condensed, JetBrains Mono
"""

import json
import os
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Embedded Abstract mark SVG base64 (matching canonical assets)
ABM_B64 = (
    "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxNjguOTQ4IDE0OS45ODEiIHJvbGU9ImltZyIgYXJpYS1sYWJlbD0iQWJzdHJhY3QiPgo8ZGVmcz48bGluZWFyR3JhZGllbnQgaWQ9ImFibS1ncmFkIiB4MT0iNjYuMDQxNyIgeTE9IjkuMDY3NCIgeDI9IjExMi45OTIiIHkyPSI1OC40NTkxIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHN0b3Agc3RvcC1jb2xvcj0iI0ZGMjE2QiIvPjxzdG9wIG9mZnNldD0iMC42NzE3MDIiIHN0b3AtY29sb3I9IiNFODAwNUQiLz48L2xpbmVhckdyYWRpZW50PjwvZGVmcz4KPHBhdGggZmlsbD0iI0U4MDA1RCIgZD0iTTE1My4yNjggMTQ2LjYyNUwxMzMuMjI4IDEwOS42MjJDMTQyLjI1IDEwNy45NzggMTUyLjY0MSAxMDcuODY0IDE2MC45NzEgMTEyLjEyOUMxNjMuMTY0IDExMy4yNTIgMTY1LjIyNiAxMTQuNzE3IDE2Ni41OTUgMTE2LjczNkMxNzEuMDY1IDEyMy4yOTcgMTY4LjUyNSAxMzQuMzY3IDE2NC4wNTUgMTQwLjI2QzE2MS42OCAxNDMuMzg1IDE1OC4zOTcgMTQ2LjIwMSAxNTQuMjkxIDE0OC42MjdDMTU0LjA2IDE0OC4xODggMTUzLjc0NiAxNDcuNTY5IDE1My4yODQgMTQ2LjYyNUgxNTMuMjY4WiIvPgo8cGF0aCBmaWxsPSIjQzIwMDRDIiBkPSJNMTYuNDA5NiAxMTguNDExQzE1LjUzNTQgMTE4LjMxMyAxNC42OTQyIDExOC4wODUgMTMuOTAyNSAxMTcuNjk0QzEyLjA4ODIgMTE2Ljc4MiAxMC43ODUyIDExNS4wNzQgMTAuMDEgMTEzLjIxOEM3LjEwNjk4IDEwNi4yMzMgOS4xNTIyOCA5Ny4yOTYgMTEuNzc0OCA5MC41NTY2QzE0LjI2NTQgODQuMTc1NCAxOC41MDQzIDc4LjM0NzEgMjIuMDE3NiA3Mi40ODY1QzI1LjQzMTkgNjUuNzQ3MSAyOS45MDE3IDU5LjM2NTYgMzMuNzk0MyA1Mi44ODY1QzM1LjkwNTUgNDkuMzUzOSAzOS4wNTU4IDQ2LjYzNTIgNDIuODgyNSA0NS4wMjM2QzQ3LjE3MDkgNDMuMjE2NiA1My43MDI1IDQxLjA4NCA2MC41MTQ1IDQxLjA4NEM2MC41MTQ1IDQxLjA4NCA2MS4wNzUzIDQxLjA4NCA2MS4yMjM3IDQxLjA4NEg2MS41ODY2SDYxLjcxODZINjIuMDQ4NUM2Ni45MzA4IDQxLjI3OTQgNzEuNjE1MSA0Mi40MzUyIDc2LjAxODkgNDQuNTE4OUM3NS40NTggNDQuMjU4NSA2OS4zMjIxIDUyLjI2NzggNjguNzc4MSA1Mi45NTE2QzY1LjQ0NTkgNTcuMDcwMyA2Mi4yOTU5IDYxLjMxOTEgNTkuMjc3NSA2NS42NjU5QzUzLjc4NSA3My41NDQ2IDQ4LjgyMDMgODEuNzY2MSA0NC4yMDIgOTAuMTgyMkM0MS45OTE4IDk0LjIwMzEgMzkuNjQ5NyA5OC4yNTY4IDM3LjY4NjkgMTAyLjM5MkMzNS43MjQxIDEwNi41MjcgMzQuNDM3NSAxMTAuNDAxIDMxLjAwNjggMTEzLjM4QzI4LjU2NTcgMTE1LjQ5NyAyNS40OTc4IDExNi43MzQgMjIuMzgwNSAxMTcuNjQ1QzIwLjQ1MDcgMTE4LjE5OSAxOC4zNzI0IDExOC42MzggMTYuNDA5NiAxMTguNDExWiIvPgo8cGF0aCBmaWxsPSJ1cmwoI2FibS1ncmFkKSIgZD0iTTEwOC40NTggNjQuNjYxQzEwMy45MjIgNTcuNDk4MSA5Ni4yODUyIDQ3LjY0OTEgODUuNDQ4NyA0MC45MDk1TDgzLjA1NzQgMzkuNDc2OUM3Ni41NTg0IDM1LjYzNSA2OS40ODI4IDMzLjU4MzggNjIuMDI3NSAzMy4zNTU5QzYxLjU2NTcgMzMuMzM5NiA2MS4wNzA4IDMzLjMzOTYgNjAuNTkyNSAzMy4zMzk2QzU0LjI0MjMgMzMuMzM5NiA0OC41MDI0IDM0LjYyNTcgNDMuNzg1MiAzNi4yMjExTDQ3LjI2NTQgMzAuNDQxOUw0OC43MTY4IDI4LjA4MTRMNTAuODQ0NiAyNC41MzI1TDUxLjgzNDIgMjIuODg4NEM1NC42MDUyIDE4LjI2NSA1Ny43MDYxIDE0LjIyNzggNjEuMDIxNCAxMC44NTc5TDYxLjM2NzcgMTAuNTE2MUM2Mi4wNjA1IDkuODQ4NjQgNjIuNzM2NSA5LjE5NzQ0IDYzLjQyOTUgOC41OTUxNUM2NC4yMDQ1IDcuOTExNDEgNjUuMDI5NSA3LjI0Mzk3IDY1Ljg4NzEgNi42MDkwOEM2Ni43Nzc5IDUuOTQxNiA2Ny42NTE4IDUuMzM5MjcgNjguNTI2MyA0Ljc4NTc3QzY4Ljg3MjUgNC41NTc4NiA2OS4xNTI5IDQuMzc4NzkgNjkuNDMzNCA0LjI0ODU2TDY5Ljg3ODQgNC4wMjA2NUw2OS45NjExIDMuOTM5MjVDNzAuMTI2MyAzLjg0MTU4IDcwLjI5MSAzLjc0MzkgNzAuNDU2MiAzLjY0NjIyTDcwLjkxNzYgMy40MTgzMkM3MS42NDM3IDMuMDQzODkgNzIuNDE4NyAyLjY2OTQ3IDczLjM3NTIgMi4yNDYyMUw3My41MjM2IDIuMTgxMDlDNzQuNzExMSAxLjcwODk5IDc1Ljc5OTcgMS4zMzQ1NyA3Ni44Mzg4IDEuMDI1MjZMNzcuMDUzNSAwLjk3NjQyM0M3Ny42MzA3IDAuODI5OTEzIDc4LjE1ODQgMC42ODMzOTYgNzguNzM2MiAwLjU4NTcyMkw4MC42OTg3IDAuMjQzODU3QzgxLjgwMzYgMC4wOTczNDM4IDgyLjkwOTEgMC4wMzIyMjY2IDg0LjAxMzkgMC4wMzIyMjY2Qzg1LjAxOTkgMC4wMzIyMjY2IDg2LjA5MjIgMC4wOTczNDM5IDg3LjIxNCAwLjIyNzU3OEM4Ny42MDk2IDAuMjc2NDE2IDg4LjAyMjEgMC4zNDE1MzMgODguNDE3OCAwLjQwNjY1TDg4LjQ1MSAwLjQzOTIwOUw4OS40NDA2IDAuNjAyMDAxQzg5LjYzODUgMC42MzQ1NTkgODkuODM2MyAwLjY4MzM5NiA5MC4wNjczIDAuNzMyMjMzQzkwLjU0NTUgMC44NDYxOSA5MC45NzQzIDAuOTYwMTQ2IDkxLjM3MDYgMS4wOTAzOEw5MS43NjYyIDEuMjA0MzRDOTIuMDYyOSAxLjMwMjAxIDkyLjM3NjUgMS4zODM0MSA5Mi42NzMzIDEuNDk3MzZMOTMuMzE2OCAxLjcyNTI3TDkzLjk1OTcgMS45Njk0NkM5NC4zNTU5IDIuMTMyMjUgOTQuNzg0NyAyLjMxMTMyIDk1LjIxMzUgMi41MDY2OEM5Ni4xMDQzIDIuODk3MzggOTcuMDExNCAzLjM1MzIgOTcuOTM0NyAzLjg5MDQxQzk4LjgyNTUgNC4zOTUwNyA5OS43MTYzIDQuOTQ4NTcgMTAwLjY3MyA1LjU5OTc0QzEwMy4zOTUgNy41MDQ0MyAxMDYuMDUgOS45MTM3MyAxMDguNTQgMTIuNzEzOEMxMDkuODI3IDE0LjE2MjYgMTExLjA5NyAxNS43OTA2IDExMi4zMzQgMTcuNTMyNEMxMTMuNzM2IDE5LjUwMjMgMTE0Ljk1NyAyMS43OTc2IDExNS45OCAyNC4zODZDMTE2LjQwOCAyNS40NDQyIDExNi43MjEgMjYuNTUxMSAxMTYuOTIgMjcuNjc0NEMxMTcuMzMyIDI5LjkzNzIgMTE3LjYxMiAzMS43NjA1IDExNy43MTEgMzIuOTMyNkMxMTcuNzQ0IDMzLjI5MDggMTE3Ljc3NyAzMy42NDg5IDExNy43NzcgMzMuOTkwOFYzNC4xODYxQzExNy44MSAzNC40MzA0IDExNy44MjcgMzQuNjU4MyAxMTcuODI3IDM0LjkxODdWMzUuMDgxNUMxMTcuODU5IDM1LjY4MzggMTE3Ljg3NiAzNi4zMDI0IDExNy44NzYgMzYuOTUzNkMxMTcuODc2IDQyLjc4MTYgMTE2LjgwNCA0OC40MTQzIDExNC42OTIgNTMuNzA1TDExNC42MjcgNTMuODY3OEMxMTQuNTc3IDUzLjk5OCAxMTQuNTI4IDU0LjExMiAxMTQuNDc4IDU0LjIyNTlMMTE0LjM5NiA1NC40MDVMMTE0LjMzIDU0LjU4NDFMMTE0LjI2NCA1NC43MzA2TDExNC4yMTQgNTQuODc3MUMxMTQuMjE0IDU0Ljg3NzEgMTE0LjE0OCA1NS4wMzk5IDExNC4xMTUgNTUuMTIxM0MxMTIuNjQ3IDU4LjQ3NDggMTEwLjc1MSA2MS42ODE4IDEwOC40NDEgNjQuNzI2MUwxMDguNDU4IDY0LjY2MVoiLz4KPHBhdGggZmlsbD0iI0ZGMjE2QiIgZD0iTTI4LjI5MyAxNDkuOTc3QzI2LjU2MTEgMTQ5Ljk3NyAyNC44MjkyIDE0OS44MyAyMy4xMzAzIDE0OS41MDVDMTkuMDA2OCAxNDguNzIzIDE1LjExNDIgMTQ2Ljk0OSAxMS43MzMgMTQ0LjUyM0M4LjM1MTcxIDE0Mi4wOTggNS4zNjYzIDEzOC44OTEgMy4yODgwNSAxMzUuMjI4QzIuODA5NzMgMTM0LjM5OCAyLjM5NzM4IDEzMy41MzUgMi4wMTgwMiAxMzIuNjU1QzEuNDI0MjMgMTMxLjIzOSAwLjk2MjQwMyAxMjkuNzkxIDAuNjMyNTI1IDEyOC4yOTNDMC41NTAwNTMgMTI3Ljg3IDAuNDY3NTgzIDEyNy40NDYgMC4zODUxMTMgMTI3LjAwN0wwLjMwMjY0MyAxMjYuNTY3QzAuMjM2NjY4IDEyNi4xNzYgMC4xODcxODYgMTI1LjcyMSAwLjEzNzcwNCAxMjUuMjQ4QzAuMDg4MjIxNSAxMjQuNzQ0IDAuMDU1MjMzNyAxMjQuMjA3IDAuMDM4NzM5NyAxMjMuNzE5VjEyMy4zMjhDMC4wMDU3NTE3OCAxMjIuODU2IC0wLjAxMDc0MjIgMTIyLjQ2NSAtMC4wMTA3NDIyIDEyMi4wOUMtMC4wMTA3NDIyIDEyMS41MjEgMC4wODgyMjE1IDExOS4xMTEgMC4xMzc3MDQgMTE4Ljc1M0MwLjEzNzcwNCAxMTguNzUzIDAuMjIwMTczIDExNy45MDcgMC4yNjk2NTYgMTE3LjYxNEwwLjQxODEwMSAxMTYuNTIzQzAuNDE4MTAxIDExNi41MjMgMC41ODMwNDEgMTE1LjUzIDAuNTgzMDQxIDExNS40OTdDMC41ODMwNDEgMTE1LjQ5NyAxLjIyNjMxIDExMi4zMjMgMS4zMDg3OCAxMTIuMDNDMS44MjAwOSAxMTUuMTg4IDIuNzkzMjMgMTE3Ljg1OCA0LjIxMTcxIDExOS45OUM2LjM1NTkzIDEyMy4wNjcgOS40ODk3NiAxMjUuMDg2IDEzLjE4NDQgMTI1Ljg2N0MxNi4zODQzIDEyNi41MzUgMTkuNzMyNSAxMjYuMjkgMjIuOTE1OSAxMjUuNjA3QzI4LjkxOTcgMTI0LjMwNCAzNC4xODEzIDEyMS40MDcgMzkuNjI0MyAxMTguNzM3QzQyLjQ3NzggMTE3LjMzNyA0NS4yNjUyIDExNS44MjMgNDguMDM2MiAxMTQuMjkzQzU2LjA2ODggMTA5LjkxNCA2My45ODU4IDEwNS4zMDcgNzEuODUzMyAxMDAuNjUxQzc4LjY2NTMgOTYuNjI5NSA4NS42NTg4IDkyLjc3MTYgOTIuMjU2OCA4OC40MjQ3TDkzLjE0NjkgODcuODcxMkw5My43OTA1IDg3LjQ5NjhMOTMuODIzNiA4Ny40NjQ2Qzk0LjEwNDEgODcuMzAxNiA5NC4zODQ1IDg3LjEyMjQgOTQuNjY1IDg2Ljk0MzNMOTUuNzIwNCA4Ni4zMDg2TDk1LjgwMyA4Ni4yMTEzQzEwMS41NzYgODIuNTMxOSAxMDYuNTczIDc4LjQ0NiAxMTAuNjk3IDc0LjAxNzlDMTE1LjMxNSA2OS4wNTI0IDExOC45MjcgNjMuNTgzIDEyMS40MTggNTcuNzM4NUMxMjMuODEgNTIuMTg3MyAxMjUuMTk1IDQ2LjI3NzkgMTI1LjU1OCA0MC4xNDA2TDEzNC4xMTggNTUuMjgwNEwxMzYuMTMxIDU4Ljc0NzlMMTUyLjE5NSA4Ny4wMDg0TDE1My4wMzcgODguNTA2NUMxNTQuNDM5IDkwLjk5NyAxNTcuOTg1IDk3LjQxMTEgMTYxLjE4NSAxMDMuODI1QzE1OS45OTcgMTAzLjM3IDE1OC43NDQgMTAyLjk3OCAxNTcuMzkxIDEwMi42MjFDMTU2LjkzIDEwMi40NzQgMTU2LjQ2OCAxMDIuMzYgMTU1Ljk5IDEwMi4yNDZDMTU1LjI2MyAxMDIuMDgzIDE1NC41NTQgMTAxLjkyIDE1My43OTUgMTAxLjc5TDE1Mi43NCAxMDEuNTk1QzE1MS44NjYgMTAxLjQ0OSAxNTAuOTI2IDEwMS4zMTggMTQ5Ljk4NiAxMDEuMjA0TDE0OS43NzEgMTAxLjE3MkgxNDkuNTU3QzE0OS4yOTMgMTAxLjEyMyAxNDkuMDEyIDEwMS4wOSAxNDguNzE1IDEwMS4wNzRDMTQ4LjMwMyAxMDEuMDI1IDE0Ny44OTEgMTAxLjAwOSAxNDcuNDc5IDEwMC45NzZDMTQ2LjE5MiAxMDAuODk1IDE0NS4wMjEgMTAwLjg2MiAxNDMuOCAxMDAuODYyQzEzOC4zMDggMTAwLjg2MiAxMzIuNDIgMTAxLjY0NCAxMjYuMzE3IDEwMy4xNzRDMTE3Ljg4OCAxMDUuMzIzIDEwOC45MTYgMTA4LjkzNyA5OS41OTY1IDExMy45NjdMOTkuMTM0NSAxMTQuMTE0TDk4LjkzNjcgMTE0LjI5M0w5OC44NzA0IDExNC4zMjVMOTguODIwOSAxMTQuMzc0Qzk0LjU5ODYgMTE2Ljg4MSA5MC4zNiAxMTkuMzg4IDg2LjEzNzEgMTIxLjg5NUM4Mi4xNjIxIDEyNC4yNTUgNzguMTg3IDEyNi42IDc0LjIxMiAxMjguOTQ0QzcwLjYgMTMxLjA3NyA2Ni45NzEyIDEzMy4yMjYgNjMuMzQyOSAxMzUuMzU4QzYwLjE3NTggMTM3LjIzIDU3LjAwOSAxMzkuMDg2IDUzLjg0MjEgMTQwLjk0MkM1MC4zNzgzIDE0Mi45NzcgNDYuOTQ3NiAxNDUuMDYxIDQzLjIzNjUgMTQ2LjY0QzQxLjMwNjcgMTQ3LjQ3IDM5LjM0MzkgMTQ4LjE3IDM3LjMxNTIgMTQ4LjcyM0MzNC4zNjI3IDE0OS41MjEgMzEuMjk0OCAxNDkuOTkzIDI4LjIyNyAxNDkuOTc3SDI4LjI5M1oiLz4KPC9zdmc+Cg=="
)

def build_drawio(title, width, height, elements):
    """Wrap elements inside standard Draw.io mxGraphModel XML."""
    cells = "\n".join(elements)
    return (
        f'<mxfile host="app.diagrams.net" type="device">'
        f'<diagram id="{title}" name="{title}">'
        f'<mxGraphModel dx="1400" dy="900" grid="0" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{width}" pageHeight="{height}" background="#060608" math="0" shadow="0">'
        f'<root><mxCell id="0"/><mxCell id="1" parent="0"/>\n{cells}\n'
        f'</root></mxGraphModel></diagram></mxfile>'
    )

def main():
    print("Generating canonical Draw.io and SVG assets...")

    # =========================================================================
    # 1. BILLING ACCOUNT DIAGRAMS
    # =========================================================================
    ba_title = "Billing account audit logs to Pub/Sub"
    ba_cells = [
        # Banner
        '<mxCell id="banner" value="&lt;span style=\'font-size:20px;color:#FF216B\'&gt;&lt;b&gt;Billing Account audit logs to Pub/Sub&lt;/b&gt;&lt;/span&gt;" style="text;html=1;align=left;verticalAlign=middle;whiteSpace=wrap;fontFamily=Barlow Semi Condensed;fontColor=#dfe3ec;fontSize=20;" vertex="1" parent="1"><mxGeometry x="40" y="18" width="700" height="50" as="geometry"/></mxCell>',
        '<mxCell id="banner-rule" value="" style="line;strokeWidth=2;html=1;strokeColor=#FF216B;" vertex="1" parent="1"><mxGeometry x="40" y="62" width="280" height="8" as="geometry"/></mxCell>',
        # Groups
        '<mxCell id="ba_group" value="GCP Billing Account (outside resource hierarchy)" style="points=[[0,0],[0.25,0],[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]];outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=12;fontStyle=0;container=1;pointerEvents=0;collapsible=0;recursiveResize=0;shape=mxgraph.aws4.group;grStroke=1;strokeColor=#F5C61E;fillColor=none;verticalAlign=top;fontColor=#F5C61E;align=left;spacingLeft=30;" vertex="1" parent="1"><mxGeometry x="40" y="90" width="460" height="580" as="geometry"/></mxCell>',
        '<mxCell id="lp" value="Dedicated logging project" style="points=[[0,0],[0.25,0],[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]];outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=12;fontStyle=0;container=1;pointerEvents=0;collapsible=0;recursiveResize=0;shape=mxgraph.aws4.group;grStroke=1;strokeColor=#01e69d;fillColor=none;verticalAlign=top;fontColor=#01e69d;align=left;spacingLeft=30;" vertex="1" parent="1"><mxGeometry x="540" y="90" width="360" height="580" as="geometry"/></mxCell>',
        '<mxCell id="abs" value="Abstract" style="points=[[0,0],[0.25,0],[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]];outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=12;fontStyle=0;container=1;pointerEvents=0;collapsible=0;recursiveResize=0;shape=mxgraph.aws4.group;grStroke=1;strokeColor=#FF216B;fillColor=none;verticalAlign=top;fontColor=#FF216B;align=left;spacingLeft=30;" vertex="1" parent="1"><mxGeometry x="940" y="90" width="220" height="580" as="geometry"/></mxCell>',
        # Nodes in BA
        '<mxCell id="bill" value="Billing Account&lt;br&gt;012345-567890-ABCDEF" style="sketch=0;html=1;outlineConnect=0;fontColor=#ECEFF1;verticalLabelPosition=bottom;verticalAlign=top;align=center;fontSize=11;fillColor=#4285F4;shape=mxgraph.gcp2.cost;" vertex="1" parent="ba_group"><mxGeometry x="50" y="160" width="78" height="78" as="geometry"/></mxCell>',
        '<mxCell id="sink" value="Billing Account Sink&lt;br&gt;abstract-billing-sink" style="sketch=0;html=1;outlineConnect=0;fontColor=#ECEFF1;verticalLabelPosition=bottom;verticalAlign=top;align=center;fontSize=11;fillColor=#4285F4;shape=mxgraph.gcp2.logging;" vertex="1" parent="ba_group"><mxGeometry x="270" y="160" width="78" height="78" as="geometry"/></mxCell>',
        '<mxCell id="types" value="Log Types&lt;br&gt;Admin Activity + System Event" style="sketch=0;html=1;outlineConnect=0;fontColor=#ECEFF1;verticalLabelPosition=bottom;verticalAlign=top;align=center;fontSize=11;fillColor=#4285F4;shape=mxgraph.gcp2.cloud_security_command_center;" vertex="1" parent="ba_group"><mxGeometry x="160" y="380" width="78" height="78" as="geometry"/></mxCell>',
        # Nodes in LP
        '<mxCell id="topic" value="Pub/Sub topic&lt;br&gt;abstract-audit-logs" style="sketch=0;html=1;outlineConnect=0;fontColor=#ECEFF1;verticalLabelPosition=bottom;verticalAlign=top;align=center;fontSize=11;fillColor=#FF216B;shape=mxgraph.gcp2.cloud_pubsub;" vertex="1" parent="lp"><mxGeometry x="50" y="160" width="78" height="78" as="geometry"/></mxCell>',
        '<mxCell id="sub" value="Pull subscription&lt;br&gt;expiration: never" style="sketch=0;html=1;outlineConnect=0;fontColor=#ECEFF1;verticalLabelPosition=bottom;verticalAlign=top;align=center;fontSize=11;fillColor=#FF216B;shape=mxgraph.gcp2.cloud_pubsub;" vertex="1" parent="lp"><mxGeometry x="210" y="160" width="78" height="78" as="geometry"/></mxCell>',
        '<mxCell id="sa" value="Reader Service Account&lt;br&gt;roles/pubsub.subscriber" style="sketch=0;html=1;outlineConnect=0;fontColor=#ECEFF1;verticalLabelPosition=bottom;verticalAlign=top;align=center;fontSize=11;fillColor=#01e69d;shape=mxgraph.gcp2.cloud_iam;" vertex="1" parent="lp"><mxGeometry x="130" y="380" width="78" height="78" as="geometry"/></mxCell>',
        # Node in Abstract
        f'<mxCell id="plat" value="Abstract platform&lt;br&gt;normalised to ACS" style="shape=image;html=1;verticalLabelPosition=bottom;verticalAlign=top;align=center;imageAspect=1;fontColor=#ECEFF1;fontSize=11;image=data:image/svg+xml,{ABM_B64};" vertex="1" parent="abs"><mxGeometry x="70" y="160" width="78" height="78" as="geometry"/></mxCell>',
        # Edges
        '<mxCell id="e1" value="billing audit events" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;jettySize=auto;orthogonalLoop=1;strokeColor=#F5C61E;strokeWidth=2;fontColor=#dfe3ec;fontFamily=Barlow;fontSize=11;labelBackgroundColor=#060608;endArrow=blockThin;endFill=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="bill" target="sink"><mxGeometry relative="1" as="geometry"/></mxCell>',
        '<mxCell id="e2" value="activity filter" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;jettySize=auto;orthogonalLoop=1;strokeColor=#7D7589;strokeWidth=2;fontColor=#dfe3ec;fontFamily=Barlow;fontSize=11;labelBackgroundColor=#060608;endArrow=blockThin;endFill=1;exitX=0.5;exitY=0;exitDx=0;exitDy=0;entryX=0.5;entryY=1;entryDx=0;entryDy=0;dashed=1;" edge="1" parent="1" source="types" target="sink"><mxGeometry relative="1" as="geometry"/></mxCell>',
        '<mxCell id="e3" value="writer identity needs&#xa;roles/pubsub.publisher" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;jettySize=auto;orthogonalLoop=1;strokeColor=#FF216B;strokeWidth=2;fontColor=#dfe3ec;fontFamily=Barlow;fontSize=11;labelBackgroundColor=#060608;endArrow=blockThin;endFill=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="sink" target="topic"><mxGeometry relative="1" as="geometry"/></mxCell>',
        '<mxCell id="e4" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;jettySize=auto;orthogonalLoop=1;strokeColor=#FF216B;strokeWidth=2;fontColor=#dfe3ec;fontFamily=Barlow;fontSize=11;labelBackgroundColor=#060608;endArrow=blockThin;endFill=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="topic" target="sub"><mxGeometry relative="1" as="geometry"/></mxCell>',
        '<mxCell id="e5" value="pull as SA" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;jettySize=auto;orthogonalLoop=1;strokeColor=#FF216B;strokeWidth=2;fontColor=#dfe3ec;fontFamily=Barlow;fontSize=11;labelBackgroundColor=#060608;endArrow=blockThin;endFill=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="sub" target="plat"><mxGeometry relative="1" as="geometry"/></mxCell>',
        '<mxCell id="e6" value="subscriber role" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;jettySize=auto;orthogonalLoop=1;strokeColor=#01e69d;strokeWidth=2;fontColor=#dfe3ec;fontFamily=Barlow;fontSize=11;labelBackgroundColor=#060608;endArrow=blockThin;endFill=1;exitX=0.5;exitY=0;exitDx=0;exitDy=0;entryX=0.5;entryY=1;entryDx=0;entryDy=0;dashed=1;" edge="1" parent="1" source="sa" target="sub"><mxGeometry relative="1" as="geometry"/></mxCell>',
        # Badges
        '<mxCell id="b0" value="NOT captured by organization-level sinks" style="rounded=1;arcSize=50;html=1;whiteSpace=wrap;fillColor=#060608;strokeColor=#F5C61E;strokeWidth=1;fontColor=#F5C61E;fontFamily=JetBrains Mono;fontSize=10;verticalAlign=middle;align=center;" vertex="1" parent="1"><mxGeometry x="50" y="110" width="290" height="26" as="geometry"/></mxCell>',
        '<mxCell id="b1" value="requires roles/logging.configWriter on billing account" style="rounded=1;arcSize=50;html=1;whiteSpace=wrap;fillColor=#060608;strokeColor=#01e69d;strokeWidth=1;fontColor=#01e69d;fontFamily=JetBrains Mono;fontSize=10;verticalAlign=middle;align=center;" vertex="1" parent="1"><mxGeometry x="50" y="620" width="370" height="26" as="geometry"/></mxCell>'
    ]
    ba_drawio = build_drawio(ba_title, 1200, 720, ba_cells)

    ba_spec = {
        "title": ba_title,
        "theme": "dark",
        "animate": False,
        "pages": [{
            "name": ba_title,
            "width": 1200,
            "height": 720,
            "banner": {"title": ba_title, "x": 40, "y": 18, "w": 700, "h": 50},
            "groups": [
                {"id": "ba_group", "label": "GCP Billing Account (outside resource hierarchy)", "kind": "plain", "x": 40, "y": 90, "w": 460, "h": 580, "color": "#F5C61E"},
                {"id": "lp", "label": "Dedicated logging project", "kind": "plain", "x": 540, "y": 90, "w": 360, "h": 580, "color": "#01E69D"},
                {"id": "abs", "label": "Abstract", "kind": "plain", "x": 940, "y": 90, "w": 220, "h": 580, "color": "#FF216B"}
            ],
            "nodes": [
                {"id": "bill", "label": "Billing Account", "sublabel": "012345-567890-ABCDEF", "icon": "gcp:cost", "parent": "ba_group", "x": 50, "y": 160},
                {"id": "sink", "label": "Billing Account Sink", "sublabel": "abstract-billing-sink", "icon": "gcp:logging", "parent": "ba_group", "x": 270, "y": 160},
                {"id": "types", "label": "Log Types", "sublabel": "Admin Activity + System Event", "icon": "gcp:cloud_security_command_center", "parent": "ba_group", "x": 160, "y": 380},
                {"id": "topic", "label": "Pub/Sub topic", "sublabel": "abstract-audit-logs", "icon": "gcp:cloud_pubsub", "parent": "lp", "x": 50, "y": 160},
                {"id": "sub", "label": "Pull subscription", "sublabel": "expiration: never", "icon": "gcp:cloud_pubsub", "parent": "lp", "x": 210, "y": 160},
                {"id": "sa", "label": "Reader Service Account", "sublabel": "roles/pubsub.subscriber", "icon": "gcp:cloud_iam", "parent": "lp", "x": 130, "y": 380},
                {"id": "plat", "label": "Abstract platform", "sublabel": "normalised to ACS", "icon": "img:../brand/abstract-logo-mark.svg", "parent": "abs", "x": 70, "y": 160}
            ]
        }]
    }

    # =========================================================================
    # 2. NETWORK THREATS DIAGRAMS
    # =========================================================================
    nt_title = "GCP Network Threat Telemetry to Abstract Security"
    nt_cells = [
        '<mxCell id="banner" value="&lt;span style=\'font-size:20px;color:#FF216B\'&gt;&lt;b&gt;GCP Network Threat Telemetry to Abstract Security&lt;/b&gt;&lt;/span&gt;" style="text;html=1;align=left;verticalAlign=middle;whiteSpace=wrap;fontFamily=Barlow Semi Condensed;fontColor=#dfe3ec;fontSize=20;" vertex="1" parent="1"><mxGeometry x="40" y="18" width="700" height="50" as="geometry"/></mxCell>',
        '<mxCell id="banner-rule" value="" style="line;strokeWidth=2;html=1;strokeColor=#FF216B;" vertex="1" parent="1"><mxGeometry x="40" y="62" width="320" height="8" as="geometry"/></mxCell>',
        '<mxCell id="org" value="Your GCP Organization / VPC Perimeter" style="points=[[0,0],[0.25,0],[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]];outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=12;fontStyle=0;container=1;pointerEvents=0;collapsible=0;recursiveResize=0;shape=mxgraph.aws4.group;grStroke=1;strokeColor=#2e9bf0;fillColor=none;verticalAlign=top;fontColor=#2e9bf0;align=left;spacingLeft=30;" vertex="1" parent="1"><mxGeometry x="40" y="90" width="560" height="610" as="geometry"/></mxCell>',
        '<mxCell id="lp" value="Dedicated logging project" style="points=[[0,0],[0.25,0],[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]];outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=12;fontStyle=0;container=1;pointerEvents=0;collapsible=0;recursiveResize=0;shape=mxgraph.aws4.group;grStroke=1;strokeColor=#01e69d;fillColor=none;verticalAlign=top;fontColor=#01e69d;align=left;spacingLeft=30;" vertex="1" parent="1"><mxGeometry x="640" y="90" width="380" height="610" as="geometry"/></mxCell>',
        '<mxCell id="abs" value="Abstract" style="points=[[0,0],[0.25,0],[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]];outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=12;fontStyle=0;container=1;pointerEvents=0;collapsible=0;recursiveResize=0;shape=mxgraph.aws4.group;grStroke=1;strokeColor=#FF216B;fillColor=none;verticalAlign=top;fontColor=#FF216B;align=left;spacingLeft=30;" vertex="1" parent="1"><mxGeometry x="1060" y="90" width="200" height="610" as="geometry"/></mxCell>',
        # Nodes in Org
        '<mxCell id="waf" value="Cloud Armor WAF&lt;br&gt;OWASP &amp; DDoS decisions" style="sketch=0;html=1;outlineConnect=0;fontColor=#ECEFF1;verticalLabelPosition=bottom;verticalAlign=top;align=center;fontSize=11;fillColor=#4285F4;shape=mxgraph.gcp2.security_scanner;" vertex="1" parent="org"><mxGeometry x="50" y="60" width="78" height="78" as="geometry"/></mxCell>',
        '<mxCell id="ids" value="Cloud IDS&lt;br&gt;Snort L4-L7 threat alerts" style="sketch=0;html=1;outlineConnect=0;fontColor=#ECEFF1;verticalLabelPosition=bottom;verticalAlign=top;align=center;fontSize=11;fillColor=#4285F4;shape=mxgraph.gcp2.cloud_security_command_center;" vertex="1" parent="org"><mxGeometry x="50" y="190" width="78" height="78" as="geometry"/></mxCell>',
        '<mxCell id="dns" value="VPC DNS Queries&lt;br&gt;DGA &amp; exfiltration lookups" style="sketch=0;html=1;outlineConnect=0;fontColor=#ECEFF1;verticalLabelPosition=bottom;verticalAlign=top;align=center;fontSize=11;fillColor=#4285F4;shape=mxgraph.gcp2.cloud_dns;" vertex="1" parent="org"><mxGeometry x="50" y="320" width="78" height="78" as="geometry"/></mxCell>',
        '<mxCell id="fw" value="VPC Firewall Rules&lt;br&gt;L3/L4 deny &amp; allow rules" style="sketch=0;html=1;outlineConnect=0;fontColor=#ECEFF1;verticalLabelPosition=bottom;verticalAlign=top;align=center;fontSize=11;fillColor=#4285F4;shape=mxgraph.gcp2.firewall_rules;" vertex="1" parent="org"><mxGeometry x="50" y="450" width="78" height="78" as="geometry"/></mxCell>',
        '<mxCell id="router" value="Log Router (Org Sink)&lt;br&gt;abstract-org-network-threats" style="sketch=0;html=1;outlineConnect=0;fontColor=#ECEFF1;verticalLabelPosition=bottom;verticalAlign=top;align=center;fontSize=11;fillColor=#4285F4;shape=mxgraph.gcp2.logging;" vertex="1" parent="org"><mxGeometry x="400" y="250" width="78" height="78" as="geometry"/></mxCell>',
        # Nodes in LP
        '<mxCell id="topic" value="Pub/Sub topic&lt;br&gt;abstract-network-threats" style="sketch=0;html=1;outlineConnect=0;fontColor=#ECEFF1;verticalLabelPosition=bottom;verticalAlign=top;align=center;fontSize=11;fillColor=#FF216B;shape=mxgraph.gcp2.cloud_pubsub;" vertex="1" parent="lp"><mxGeometry x="50" y="250" width="78" height="78" as="geometry"/></mxCell>',
        '<mxCell id="sub" value="Pull subscription&lt;br&gt;expiration: never" style="sketch=0;html=1;outlineConnect=0;fontColor=#ECEFF1;verticalLabelPosition=bottom;verticalAlign=top;align=center;fontSize=11;fillColor=#FF216B;shape=mxgraph.gcp2.cloud_pubsub;" vertex="1" parent="lp"><mxGeometry x="220" y="250" width="78" height="78" as="geometry"/></mxCell>',
        '<mxCell id="sa" value="Reader Service Account&lt;br&gt;roles/pubsub.subscriber" style="sketch=0;html=1;outlineConnect=0;fontColor=#ECEFF1;verticalLabelPosition=bottom;verticalAlign=top;align=center;fontSize=11;fillColor=#01e69d;shape=mxgraph.gcp2.cloud_iam;" vertex="1" parent="lp"><mxGeometry x="135" y="420" width="78" height="78" as="geometry"/></mxCell>',
        # Node in Abstract
        f'<mxCell id="plat" value="Abstract platform&lt;br&gt;ECS network schema" style="shape=image;html=1;verticalLabelPosition=bottom;verticalAlign=top;align=center;imageAspect=1;fontColor=#ECEFF1;fontSize=11;image=data:image/svg+xml,{ABM_B64};" vertex="1" parent="abs"><mxGeometry x="60" y="250" width="78" height="78" as="geometry"/></mxCell>',
        # Edges
        '<mxCell id="e1" value="ALLOW / DENY actions" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;jettySize=auto;orthogonalLoop=1;strokeColor=#2E9BF0;strokeWidth=2;fontColor=#dfe3ec;fontFamily=Barlow;fontSize=11;labelBackgroundColor=#060608;endArrow=blockThin;endFill=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.2;entryDx=0;entryDy=0;" edge="1" parent="1" source="waf" target="router"><mxGeometry relative="1" as="geometry"/></mxCell>',
        '<mxCell id="e2" value="threat exploits" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;jettySize=auto;orthogonalLoop=1;strokeColor=#FF216B;strokeWidth=2;fontColor=#dfe3ec;fontFamily=Barlow;fontSize=11;labelBackgroundColor=#060608;endArrow=blockThin;endFill=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.4;entryDx=0;entryDy=0;" edge="1" parent="1" source="ids" target="router"><mxGeometry relative="1" as="geometry"/></mxCell>',
        '<mxCell id="e3" value="dns_queries" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;jettySize=auto;orthogonalLoop=1;strokeColor=#F5C61E;strokeWidth=2;fontColor=#dfe3ec;fontFamily=Barlow;fontSize=11;labelBackgroundColor=#060608;endArrow=blockThin;endFill=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.6;entryDx=0;entryDy=0;" edge="1" parent="1" source="dns" target="router"><mxGeometry relative="1" as="geometry"/></mxCell>',
        '<mxCell id="e4" value="firewall rule logs" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;jettySize=auto;orthogonalLoop=1;strokeColor=#01e69d;strokeWidth=2;fontColor=#dfe3ec;fontFamily=Barlow;fontSize=11;labelBackgroundColor=#060608;endArrow=blockThin;endFill=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.8;entryDx=0;entryDy=0;" edge="1" parent="1" source="fw" target="router"><mxGeometry relative="1" as="geometry"/></mxCell>',
        '<mxCell id="e5" value="writer identity needs&#xa;roles/pubsub.publisher" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;jettySize=auto;orthogonalLoop=1;strokeColor=#FF216B;strokeWidth=2;fontColor=#dfe3ec;fontFamily=Barlow;fontSize=11;labelBackgroundColor=#060608;endArrow=blockThin;endFill=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="router" target="topic"><mxGeometry relative="1" as="geometry"/></mxCell>',
        '<mxCell id="e6" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;jettySize=auto;orthogonalLoop=1;strokeColor=#FF216B;strokeWidth=2;fontColor=#dfe3ec;fontFamily=Barlow;fontSize=11;labelBackgroundColor=#060608;endArrow=blockThin;endFill=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="topic" target="sub"><mxGeometry relative="1" as="geometry"/></mxCell>',
        '<mxCell id="e7" value="pull stream" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;jettySize=auto;orthogonalLoop=1;strokeColor=#FF216B;strokeWidth=2;fontColor=#dfe3ec;fontFamily=Barlow;fontSize=11;labelBackgroundColor=#060608;endArrow=blockThin;endFill=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="sub" target="plat"><mxGeometry relative="1" as="geometry"/></mxCell>',
        '<mxCell id="e8" value="subscriber role" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;jettySize=auto;orthogonalLoop=1;strokeColor=#01e69d;strokeWidth=2;fontColor=#dfe3ec;fontFamily=Barlow;fontSize=11;labelBackgroundColor=#060608;endArrow=blockThin;endFill=1;exitX=0.5;exitY=0;exitDx=0;exitDy=0;entryX=0.5;entryY=1;entryDx=0;entryDy=0;dashed=1;" edge="1" parent="1" source="sa" target="sub"><mxGeometry relative="1" as="geometry"/></mxCell>',
        # Badges
        '<mxCell id="b0" value="--include-children · covers every project perimeter" style="rounded=1;arcSize=50;html=1;whiteSpace=wrap;fillColor=#060608;strokeColor=#2e9bf0;strokeWidth=1;fontColor=#2e9bf0;fontFamily=JetBrains Mono;fontSize=10;verticalAlign=middle;align=center;" vertex="1" parent="1"><mxGeometry x="50" y="110" width="340" height="26" as="geometry"/></mxCell>',
        '<mxCell id="b1" value="normalized to ACS network fields: source.ip, dest.ip, threat.indicator" style="rounded=1;arcSize=50;html=1;whiteSpace=wrap;fillColor=#060608;strokeColor=#01e69d;strokeWidth=1;fontColor=#01e69d;fontFamily=JetBrains Mono;fontSize=10;verticalAlign=middle;align=center;" vertex="1" parent="1"><mxGeometry x="640" y="650" width="450" height="26" as="geometry"/></mxCell>'
    ]
    nt_drawio = build_drawio(nt_title, 1300, 740, nt_cells)

    nt_spec = {
        "title": nt_title,
        "theme": "dark",
        "animate": False,
        "pages": [{
            "name": nt_title,
            "width": 1300,
            "height": 740,
            "banner": {"title": nt_title, "x": 40, "y": 18, "w": 700, "h": 50},
            "groups": [
                {"id": "org", "label": "Your GCP Organization / VPC Perimeter", "kind": "plain", "x": 40, "y": 90, "w": 560, "h": 610, "color": "#2E9BF0"},
                {"id": "lp", "label": "Dedicated logging project", "kind": "plain", "x": 640, "y": 90, "w": 380, "h": 610, "color": "#01E69D"},
                {"id": "abs", "label": "Abstract", "kind": "plain", "x": 1060, "y": 90, "w": 200, "h": 610, "color": "#FF216B"}
            ],
            "nodes": [
                {"id": "waf", "label": "Cloud Armor WAF", "sublabel": "OWASP & DDoS decisions", "icon": "gcp:security_scanner", "parent": "org", "x": 50, "y": 60},
                {"id": "ids", "label": "Cloud IDS", "sublabel": "Snort L4-L7 threat alerts", "icon": "gcp:cloud_security_command_center", "parent": "org", "x": 50, "y": 190},
                {"id": "dns", "label": "VPC DNS Queries", "sublabel": "DGA & exfiltration lookups", "icon": "gcp:cloud_dns", "parent": "org", "x": 50, "y": 320},
                {"id": "fw", "label": "VPC Firewall Rules", "sublabel": "L3/L4 deny & allow rules", "icon": "gcp:firewall_rules", "parent": "org", "x": 50, "y": 450},
                {"id": "router", "label": "Log Router (Org Sink)", "sublabel": "abstract-org-network-threats", "icon": "gcp:logging", "parent": "org", "x": 400, "y": 250},
                {"id": "topic", "label": "Pub/Sub topic", "sublabel": "abstract-network-threats", "icon": "gcp:cloud_pubsub", "parent": "lp", "x": 50, "y": 250},
                {"id": "sub", "label": "Pull subscription", "sublabel": "expiration: never", "icon": "gcp:cloud_pubsub", "parent": "lp", "x": 220, "y": 250},
                {"id": "sa", "label": "Reader Service Account", "sublabel": "roles/pubsub.subscriber", "icon": "gcp:cloud_iam", "parent": "lp", "x": 135, "y": 420},
                {"id": "plat", "label": "Abstract platform", "sublabel": "ECS network schema", "icon": "img:../brand/abstract-logo-mark.svg", "parent": "abs", "x": 60, "y": 250}
            ]
        }]
    }

    # =========================================================================
    # 3. IDENTITY & AUTHENTICATION DIAGRAMS
    # =========================================================================
    id_title = "GCP & Workspace Identity Authentication Auditing Architecture"
    id_cells = [
        '<mxCell id="banner" value="&lt;span style=\'font-size:20px;color:#FF216B\'&gt;&lt;b&gt;GCP &amp; Workspace Identity Authentication Auditing Architecture&lt;/b&gt;&lt;/span&gt;" style="text;html=1;align=left;verticalAlign=middle;whiteSpace=wrap;fontFamily=Barlow Semi Condensed;fontColor=#dfe3ec;fontSize=20;" vertex="1" parent="1"><mxGeometry x="40" y="18" width="800" height="50" as="geometry"/></mxCell>',
        '<mxCell id="banner-rule" value="" style="line;strokeWidth=2;html=1;strokeColor=#FF216B;" vertex="1" parent="1"><mxGeometry x="40" y="62" width="380" height="8" as="geometry"/></mxCell>',
        # Groups
        '<mxCell id="id_sources" value="5 Identity &amp; Authentication Streams" style="points=[[0,0],[0.25,0],[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]];outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=12;fontStyle=0;container=1;pointerEvents=0;collapsible=0;recursiveResize=0;shape=mxgraph.aws4.group;grStroke=1;strokeColor=#2e9bf0;fillColor=none;verticalAlign=top;fontColor=#2e9bf0;align=left;spacingLeft=30;" vertex="1" parent="1"><mxGeometry x="40" y="90" width="380" height="660" as="geometry"/></mxCell>',
        '<mxCell id="pipe" value="GCP Aggregation &amp; Dedicated Pipeline" style="points=[[0,0],[0.25,0],[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]];outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=12;fontStyle=0;container=1;pointerEvents=0;collapsible=0;recursiveResize=0;shape=mxgraph.aws4.group;grStroke=1;strokeColor=#01e69d;fillColor=none;verticalAlign=top;fontColor=#01e69d;align=left;spacingLeft=30;" vertex="1" parent="1"><mxGeometry x="460" y="90" width="460" height="660" as="geometry"/></mxCell>',
        '<mxCell id="abs" value="Abstract Security SIEM" style="points=[[0,0],[0.25,0],[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]];outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=12;fontStyle=0;container=1;pointerEvents=0;collapsible=0;recursiveResize=0;shape=mxgraph.aws4.group;grStroke=1;strokeColor=#FF216B;fillColor=none;verticalAlign=top;fontColor=#FF216B;align=left;spacingLeft=30;" vertex="1" parent="1"><mxGeometry x="960" y="90" width="400" height="420" as="geometry"/></mxCell>',
        '<mxCell id="oneuptime" value="OneUptime Zero-Silent-Failure Monitoring" style="points=[[0,0],[0.25,0],[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]];outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=12;fontStyle=0;container=1;pointerEvents=0;collapsible=0;recursiveResize=0;shape=mxgraph.aws4.group;grStroke=1;strokeColor=#F5C61E;fillColor=none;verticalAlign=top;fontColor=#F5C61E;align=left;spacingLeft=30;" vertex="1" parent="1"><mxGeometry x="960" y="530" width="400" height="220" as="geometry"/></mxCell>',
        # Nodes in id_sources
        '<mxCell id="n_login" value="User Logins&lt;br&gt;login.googleapis.com (2SV)" style="sketch=0;html=1;outlineConnect=0;fontColor=#ECEFF1;verticalLabelPosition=bottom;verticalAlign=top;align=center;fontSize=11;fillColor=#4285F4;shape=mxgraph.gcp2.users;" vertex="1" parent="id_sources"><mxGeometry x="30" y="40" width="68" height="68" as="geometry"/></mxCell>',
        '<mxCell id="n_impers" value="SA Impersonation&lt;br&gt;iamcredentials (Data Access)" style="sketch=0;html=1;outlineConnect=0;fontColor=#ECEFF1;verticalLabelPosition=bottom;verticalAlign=top;align=center;fontSize=11;fillColor=#4285F4;shape=mxgraph.gcp2.cloud_iam;" vertex="1" parent="id_sources"><mxGeometry x="30" y="160" width="68" height="68" as="geometry"/></mxCell>',
        '<mxCell id="n_wif" value="Workload Identity (WIF)&lt;br&gt;sts.googleapis.com" style="sketch=0;html=1;outlineConnect=0;fontColor=#ECEFF1;verticalLabelPosition=bottom;verticalAlign=top;align=center;fontSize=11;fillColor=#4285F4;shape=mxgraph.gcp2.cloud_iam;" vertex="1" parent="id_sources"><mxGeometry x="30" y="280" width="68" height="68" as="geometry"/></mxCell>',
        '<mxCell id="n_keys" value="Static SA Key Auth&lt;br&gt;serviceAccountKeyName" style="sketch=0;html=1;outlineConnect=0;fontColor=#ECEFF1;verticalLabelPosition=bottom;verticalAlign=top;align=center;fontSize=11;fillColor=#4285F4;shape=mxgraph.gcp2.cloud_iam;" vertex="1" parent="id_sources"><mxGeometry x="30" y="400" width="68" height="68" as="geometry"/></mxCell>',
        '<mxCell id="n_iam" value="IAM Changes &amp; Denials&lt;br&gt;SetIamPolicy, CreateRole" style="sketch=0;html=1;outlineConnect=0;fontColor=#ECEFF1;verticalLabelPosition=bottom;verticalAlign=top;align=center;fontSize=11;fillColor=#4285F4;shape=mxgraph.gcp2.cloud_iam;" vertex="1" parent="id_sources"><mxGeometry x="30" y="520" width="68" height="68" as="geometry"/></mxCell>',
        # Nodes in pipe
        '<mxCell id="p_sharing" value="Workspace Cloud Audit&lt;br&gt;native sharing (zero polling)" style="sketch=0;html=1;outlineConnect=0;fontColor=#ECEFF1;verticalLabelPosition=bottom;verticalAlign=top;align=center;fontSize=11;fillColor=#4285F4;shape=mxgraph.gcp2.cloud_apis;" vertex="1" parent="pipe"><mxGeometry x="40" y="80" width="78" height="78" as="geometry"/></mxCell>',
        '<mxCell id="p_router" value="Organization Log Router&lt;br&gt;aggregated sink" style="sketch=0;html=1;outlineConnect=0;fontColor=#ECEFF1;verticalLabelPosition=bottom;verticalAlign=top;align=center;fontSize=11;fillColor=#4285F4;shape=mxgraph.gcp2.logging;" vertex="1" parent="pipe"><mxGeometry x="40" y="320" width="78" height="78" as="geometry"/></mxCell>',
        '<mxCell id="p_topic" value="Pub/Sub topic&lt;br&gt;abstract-audit-logs" style="sketch=0;html=1;outlineConnect=0;fontColor=#ECEFF1;verticalLabelPosition=bottom;verticalAlign=top;align=center;fontSize=11;fillColor=#FF216B;shape=mxgraph.gcp2.cloud_pubsub;" vertex="1" parent="pipe"><mxGeometry x="280" y="200" width="78" height="78" as="geometry"/></mxCell>',
        '<mxCell id="p_sub" value="Pull subscription&lt;br&gt;expiration: never" style="sketch=0;html=1;outlineConnect=0;fontColor=#ECEFF1;verticalLabelPosition=bottom;verticalAlign=top;align=center;fontSize=11;fillColor=#FF216B;shape=mxgraph.gcp2.cloud_pubsub;" vertex="1" parent="pipe"><mxGeometry x="280" y="420" width="78" height="78" as="geometry"/></mxCell>',
        # Nodes in Abstract
        f'<mxCell id="plat" value="Abstract SIEM Engine&lt;br&gt;ECS gcp.identity_auth" style="shape=image;html=1;verticalLabelPosition=bottom;verticalAlign=top;align=center;imageAspect=1;fontColor=#ECEFF1;fontSize=11;image=data:image/svg+xml,{ABM_B64};" vertex="1" parent="abs"><mxGeometry x="160" y="80" width="78" height="78" as="geometry"/></mxCell>',
        '<mxCell id="rules" value="6 Detection Rules&lt;br&gt;Brute Force · Key Abuse · Geo Anomaly" style="sketch=0;html=1;outlineConnect=0;fontColor=#ECEFF1;verticalLabelPosition=bottom;verticalAlign=top;align=center;fontSize=11;fillColor=#FF216B;shape=mxgraph.gcp2.cloud_security_command_center;" vertex="1" parent="abs"><mxGeometry x="160" y="240" width="78" height="78" as="geometry"/></mxCell>',
        # Nodes in OneUptime
        '<mxCell id="probe" value="Synthetic Canary Probe&lt;br&gt;backlog &amp; latency probe" style="sketch=0;html=1;outlineConnect=0;fontColor=#ECEFF1;verticalLabelPosition=bottom;verticalAlign=top;align=center;fontSize=11;fillColor=#F5C61E;shape=mxgraph.gcp3.observability;" vertex="1" parent="oneuptime"><mxGeometry x="60" y="60" width="78" height="78" as="geometry"/></mxCell>',
        '<mxCell id="alert" value="Zero-Silent-Failure&lt;br&gt;Instant Oncall Page" style="sketch=0;html=1;outlineConnect=0;fontColor=#ECEFF1;verticalLabelPosition=bottom;verticalAlign=top;align=center;fontSize=11;fillColor=#F5C61E;shape=mxgraph.gcp2.users;" vertex="1" parent="oneuptime"><mxGeometry x="240" y="60" width="78" height="78" as="geometry"/></mxCell>',
        # Edges
        '<mxCell id="e1" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;jettySize=auto;orthogonalLoop=1;strokeColor=#2E9BF0;strokeWidth=2;fontColor=#dfe3ec;fontFamily=Barlow;fontSize=11;labelBackgroundColor=#060608;endArrow=blockThin;endFill=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="n_login" target="p_sharing"><mxGeometry relative="1" as="geometry"/></mxCell>',
        '<mxCell id="e2" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;jettySize=auto;orthogonalLoop=1;strokeColor=#2E9BF0;strokeWidth=2;fontColor=#dfe3ec;fontFamily=Barlow;fontSize=11;labelBackgroundColor=#060608;endArrow=blockThin;endFill=1;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="p_sharing" target="p_router"><mxGeometry relative="1" as="geometry"/></mxCell>',
        '<mxCell id="e3" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;jettySize=auto;orthogonalLoop=1;strokeColor=#7D7589;strokeWidth=2;fontColor=#dfe3ec;fontFamily=Barlow;fontSize=11;labelBackgroundColor=#060608;endArrow=blockThin;endFill=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="n_impers" target="p_router"><mxGeometry relative="1" as="geometry"/></mxCell>',
        '<mxCell id="e4" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;jettySize=auto;orthogonalLoop=1;strokeColor=#7D7589;strokeWidth=2;fontColor=#dfe3ec;fontFamily=Barlow;fontSize=11;labelBackgroundColor=#060608;endArrow=blockThin;endFill=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="n_wif" target="p_router"><mxGeometry relative="1" as="geometry"/></mxCell>',
        '<mxCell id="e5" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;jettySize=auto;orthogonalLoop=1;strokeColor=#7D7589;strokeWidth=2;fontColor=#dfe3ec;fontFamily=Barlow;fontSize=11;labelBackgroundColor=#060608;endArrow=blockThin;endFill=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="n_keys" target="p_router"><mxGeometry relative="1" as="geometry"/></mxCell>',
        '<mxCell id="e6" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;jettySize=auto;orthogonalLoop=1;strokeColor=#7D7589;strokeWidth=2;fontColor=#dfe3ec;fontFamily=Barlow;fontSize=11;labelBackgroundColor=#060608;endArrow=blockThin;endFill=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="n_iam" target="p_router"><mxGeometry relative="1" as="geometry"/></mxCell>',
        '<mxCell id="e7" value="writer identity" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;jettySize=auto;orthogonalLoop=1;strokeColor=#FF216B;strokeWidth=2;fontColor=#dfe3ec;fontFamily=Barlow;fontSize=11;labelBackgroundColor=#060608;endArrow=blockThin;endFill=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="p_router" target="p_topic"><mxGeometry relative="1" as="geometry"/></mxCell>',
        '<mxCell id="e8" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;jettySize=auto;orthogonalLoop=1;strokeColor=#FF216B;strokeWidth=2;fontColor=#dfe3ec;fontFamily=Barlow;fontSize=11;labelBackgroundColor=#060608;endArrow=blockThin;endFill=1;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="p_topic" target="p_sub"><mxGeometry relative="1" as="geometry"/></mxCell>',
        '<mxCell id="e9" value="pull stream" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;jettySize=auto;orthogonalLoop=1;strokeColor=#FF216B;strokeWidth=2;fontColor=#dfe3ec;fontFamily=Barlow;fontSize=11;labelBackgroundColor=#060608;endArrow=blockThin;endFill=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="p_sub" target="plat"><mxGeometry relative="1" as="geometry"/></mxCell>',
        '<mxCell id="e10" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;jettySize=auto;orthogonalLoop=1;strokeColor=#FF216B;strokeWidth=2;fontColor=#dfe3ec;fontFamily=Barlow;fontSize=11;labelBackgroundColor=#060608;endArrow=blockThin;endFill=1;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="plat" target="rules"><mxGeometry relative="1" as="geometry"/></mxCell>',
        '<mxCell id="e11" value="tests backlog lag" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;jettySize=auto;orthogonalLoop=1;strokeColor=#F5C61E;strokeWidth=2;fontColor=#dfe3ec;fontFamily=Barlow;fontSize=11;labelBackgroundColor=#060608;endArrow=blockThin;endFill=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;dashed=1;" edge="1" parent="1" source="p_sub" target="probe"><mxGeometry relative="1" as="geometry"/></mxCell>',
        '<mxCell id="e12" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;jettySize=auto;orthogonalLoop=1;strokeColor=#F5C61E;strokeWidth=2;fontColor=#dfe3ec;fontFamily=Barlow;fontSize=11;labelBackgroundColor=#060608;endArrow=blockThin;endFill=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="probe" target="alert"><mxGeometry relative="1" as="geometry"/></mxCell>',
        # Badges
        '<mxCell id="b0" value="Dual Ingestion: Native Org Cloud Audit (zero polling) + Reports API" style="rounded=1;arcSize=50;html=1;whiteSpace=wrap;fillColor=#060608;strokeColor=#2e9bf0;strokeWidth=1;fontColor=#2e9bf0;fontFamily=JetBrains Mono;fontSize=10;verticalAlign=middle;align=center;" vertex="1" parent="1"><mxGeometry x="40" y="760" width="460" height="26" as="geometry"/></mxCell>',
        '<mxCell id="b1" value="Zero-Silent-Failure: synthetic probes guarantee telemetry integrity" style="rounded=1;arcSize=50;html=1;whiteSpace=wrap;fillColor=#060608;strokeColor=#F5C61E;strokeWidth=1;fontColor=#F5C61E;fontFamily=JetBrains Mono;fontSize=10;verticalAlign=middle;align=center;" vertex="1" parent="1"><mxGeometry x="540" y="760" width="480" height="26" as="geometry"/></mxCell>'
    ]
    id_drawio = build_drawio(id_title, 1400, 800, id_cells)

    id_spec = {
        "title": id_title,
        "theme": "dark",
        "animate": False,
        "pages": [{
            "name": id_title,
            "width": 1400,
            "height": 800,
            "banner": {"title": id_title, "x": 40, "y": 18, "w": 800, "h": 50},
            "groups": [
                {"id": "id_sources", "label": "5 Identity & Authentication Streams", "kind": "plain", "x": 40, "y": 90, "w": 380, "h": 660, "color": "#2E9BF0"},
                {"id": "pipe", "label": "GCP Aggregation & Dedicated Pipeline", "kind": "plain", "x": 460, "y": 90, "w": 460, "h": 660, "color": "#01E69D"},
                {"id": "abs", "label": "Abstract Security SIEM", "kind": "plain", "x": 960, "y": 90, "w": 400, "h": 420, "color": "#FF216B"},
                {"id": "oneuptime", "label": "OneUptime Zero-Silent-Failure Monitoring", "kind": "plain", "x": 960, "y": 530, "w": 400, "h": 220, "color": "#F5C61E"}
            ],
            "nodes": [
                {"id": "n_login", "label": "User Logins", "sublabel": "login.googleapis.com", "icon": "gcp:users", "parent": "id_sources", "x": 30, "y": 40},
                {"id": "n_impers", "label": "SA Impersonation", "sublabel": "iamcredentials", "icon": "gcp:cloud_iam", "parent": "id_sources", "x": 30, "y": 160},
                {"id": "n_wif", "label": "Workload Identity (WIF)", "sublabel": "sts.googleapis.com", "icon": "gcp:cloud_iam", "parent": "id_sources", "x": 30, "y": 280},
                {"id": "n_keys", "label": "Static SA Key Auth", "sublabel": "serviceAccountKeyName", "icon": "gcp:cloud_iam", "parent": "id_sources", "x": 30, "y": 400},
                {"id": "n_iam", "label": "IAM Changes & Denials", "sublabel": "SetIamPolicy, CreateRole", "icon": "gcp:cloud_iam", "parent": "id_sources", "x": 30, "y": 520},
                {"id": "p_sharing", "label": "Workspace Cloud Audit", "sublabel": "native sharing", "icon": "gcp:cloud_apis", "parent": "pipe", "x": 40, "y": 80},
                {"id": "p_router", "label": "Organization Log Router", "sublabel": "aggregated sink", "icon": "gcp:logging", "parent": "pipe", "x": 40, "y": 320},
                {"id": "p_topic", "label": "Pub/Sub topic", "sublabel": "abstract-audit-logs", "icon": "gcp:cloud_pubsub", "parent": "pipe", "x": 280, "y": 200},
                {"id": "p_sub", "label": "Pull subscription", "sublabel": "expiration: never", "icon": "gcp:cloud_pubsub", "parent": "pipe", "x": 280, "y": 420},
                {"id": "plat", "label": "Abstract SIEM Engine", "sublabel": "ECS gcp.identity_auth", "icon": "img:../brand/abstract-logo-mark.svg", "parent": "abs", "x": 160, "y": 80},
                {"id": "rules", "label": "6 Detection Rules", "sublabel": "Brute Force · Key Abuse", "icon": "gcp:cloud_security_command_center", "parent": "abs", "x": 160, "y": 240},
                {"id": "probe", "label": "Synthetic Canary Probe", "sublabel": "backlog & latency", "icon": "gcp:observability", "parent": "oneuptime", "x": 60, "y": 60},
                {"id": "alert", "label": "Zero-Silent-Failure", "sublabel": "Instant Oncall Page", "icon": "gcp:users", "parent": "oneuptime", "x": 240, "y": 60}
            ]
        }]
    }

    # Helper function to generate clean standalone SVGs with embedded Draw.io XML
    def generate_svg(title, width, height, drawio_xml, svg_body):
        from xml.sax.saxutils import escape
        escaped_xml = escape(drawio_xml)
        return (
            f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'version="1.1" width="{width}px" height="{height}px" viewBox="0 0 {width} {height}" '
            f'content="{escaped_xml}" '
            f'style="background: #060608; background-color: light-dark(#060608, #e8e8ea); color-scheme: light dark;">\n'
            f'<title>{title}</title>\n'
            f'<defs>\n'
            f'  <linearGradient id="abm-grad" x1="0%" y1="0%" x2="100%" y2="100%"><stop stop-color="#FF216B"/><stop offset="67%" stop-color="#E8005D"/><stop offset="100%" stop-color="#C2004C"/></linearGradient>\n'
            f'  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>\n'
            f'  <style>\n'
            f'    .lbl{{font-family:Barlow,\'Barlow Semi Condensed\',-apple-system,sans-serif}}\n'
            f'    .mono{{font-family:\'JetBrains Mono\',monospace}}\n'
            f'    .box{{fill:#0d0f14;stroke-width:1.5;rx:8}}\n'
            f'    .wire{{stroke-width:2;fill:none}}\n'
            f'  </style>\n'
            f'</defs>\n'
            f'<rect width="100%" height="100%" fill="#060608"/>\n'
            f'{svg_body}\n'
            f'</svg>'
        )

    # 1. Billing Account SVG body
    ba_svg_body = """
  <!-- Banner -->
  <text class="lbl" x="40" y="48" font-size="22" font-weight="700" fill="#FF216B">Billing Account audit logs to Pub/Sub</text>
  <line x1="40" y1="62" x2="360" y2="62" stroke="#FF216B" stroke-width="2"/>

  <!-- Containers -->
  <rect x="40" y="90" width="460" height="580" rx="12" fill="none" stroke="#F5C61E" stroke-width="1.5" opacity=".6"/>
  <text class="lbl" x="64" y="122" font-size="14" font-weight="600" fill="#F5C61E">GCP Billing Account (outside resource hierarchy)</text>

  <rect x="540" y="90" width="360" height="580" rx="12" fill="none" stroke="#01e69d" stroke-width="1.5" opacity=".6"/>
  <text class="lbl" x="564" y="122" font-size="14" font-weight="600" fill="#01e69d">Dedicated logging project</text>

  <rect x="940" y="90" width="220" height="580" rx="12" fill="none" stroke="#FF216B" stroke-width="1.5" opacity=".6"/>
  <text class="lbl" x="964" y="122" font-size="14" font-weight="600" fill="#FF216B">Abstract Security</text>

  <!-- Wires -->
  <path d="M168,290 H310" class="wire" stroke="#F5C61E"/>
  <path d="M200,470 V330" class="wire" stroke="#7D7589" stroke-dasharray="6 4"/>
  <path d="M388,290 H590" class="wire" stroke="#FF216B"/>
  <path d="M668,290 H750" class="wire" stroke="#FF216B"/>
  <path d="M828,290 H1010" class="wire" stroke="#FF216B"/>
  <path d="M710,470 V330" class="wire" stroke="#01e69d" stroke-dasharray="6 4"/>

  <!-- Nodes in Billing Account -->
  <g class="lbl">
    <rect class="box" x="90" y="250" width="78" height="78" stroke="#F5C61E"/>
    <text x="129" y="295" text-anchor="middle" fill="#FFFFFF" font-size="24">💳</text>
    <text x="129" y="348" text-anchor="middle" fill="#e9ecf1" font-size="11.5" font-weight="600">Billing Account</text>
    <text x="129" y="364" text-anchor="middle" fill="#8b8f98" font-size="10">012345-567890-ABCDEF</text>

    <rect class="box" x="310" y="250" width="78" height="78" stroke="#2E9BF0"/>
    <text x="349" y="295" text-anchor="middle" fill="#FFFFFF" font-size="24">📋</text>
    <text x="349" y="348" text-anchor="middle" fill="#e9ecf1" font-size="11.5" font-weight="600">Billing Sink</text>
    <text x="349" y="364" text-anchor="middle" fill="#8b8f98" font-size="10">abstract-billing-sink</text>

    <rect class="box" x="160" y="470" width="80" height="78" stroke="#7D7589"/>
    <text x="200" y="515" text-anchor="middle" fill="#FFFFFF" font-size="24">🛡️</text>
    <text x="200" y="568" text-anchor="middle" fill="#e9ecf1" font-size="11" font-weight="600">Log Types</text>
    <text x="200" y="584" text-anchor="middle" fill="#8b8f98" font-size="10">Admin Activity + System</text>
  </g>

  <!-- Nodes in Logging Project -->
  <g class="lbl">
    <rect class="box" x="590" y="250" width="78" height="78" stroke="#FF216B"/>
    <text x="629" y="295" text-anchor="middle" fill="#FFFFFF" font-size="24">📨</text>
    <text x="629" y="348" text-anchor="middle" fill="#e9ecf1" font-size="11.5" font-weight="600">Pub/Sub Topic</text>
    <text x="629" y="364" text-anchor="middle" fill="#8b8f98" font-size="10">abstract-audit-logs</text>

    <rect class="box" x="750" y="250" width="78" height="78" stroke="#FF216B"/>
    <text x="789" y="295" text-anchor="middle" fill="#FFFFFF" font-size="24">📥</text>
    <text x="789" y="348" text-anchor="middle" fill="#e9ecf1" font-size="11.5" font-weight="600">Pull Subscription</text>
    <text x="789" y="364" text-anchor="middle" fill="#8b8f98" font-size="10">never expires</text>

    <rect class="box" x="670" y="470" width="80" height="78" stroke="#01e69d"/>
    <text x="710" y="515" text-anchor="middle" fill="#FFFFFF" font-size="24">🔑</text>
    <text x="710" y="568" text-anchor="middle" fill="#e9ecf1" font-size="11" font-weight="600">Service Account</text>
    <text x="710" y="584" text-anchor="middle" fill="#01e69d" font-size="10">roles/pubsub.subscriber</text>
  </g>

  <!-- Nodes in Abstract -->
  <g class="lbl">
    <rect class="box" x="1010" y="250" width="80" height="78" stroke="#FF216B"/>
    <path fill="url(#abm-grad)" transform="translate(1026, 268) scale(0.32)" d="M153.268 146.625L133.228 109.622C142.25 107.978 152.641 107.864 160.971 112.129C163.164 113.252 165.226 114.717 166.595 116.736C171.065 123.297 168.525 134.367 164.055 140.26C161.68 143.385 158.397 146.201 154.291 148.627C154.06 148.188 153.746 147.569 153.284 146.625H153.268Z"/>
    <path fill="#C2004C" transform="translate(1026, 268) scale(0.32)" d="M16.4096 118.411C15.5354 118.313 14.6942 118.085 13.9025 117.694C12.0882 116.782 10.7852 115.074 10.01 113.218C7.10698 106.233 9.15228 97.296 11.7748 90.5566C14.2654 84.1754 18.5043 78.3471 22.0176 72.4865C25.4319 65.7471 29.9017 59.3656 33.7943 52.8865C35.9055 49.3539 39.0558 46.6352 42.8825 45.0236C47.1709 43.2166 53.7025 41.084 60.5145 41.084C60.5145 41.084 61.0753 41.084 61.2237 41.084H61.5866H61.7186H62.0485C66.9308 41.2794 71.6151 42.4352 76.0189 44.5189C75.458 44.2585 69.3221 52.2678 68.7781 52.9516C65.4459 57.0703 62.2959 61.3191 59.2775 65.6659C53.785 73.5446 48.8203 81.7661 44.202 90.1822C41.9918 94.2031 39.6497 98.2568 37.6869 102.392C35.7241 106.527 34.4375 110.401 31.0068 113.38C28.5657 115.497 25.4978 116.734 22.3805 117.645C20.4507 118.199 18.3724 118.638 16.4096 118.411Z"/>
    <path fill="#FF216B" transform="translate(1026, 268) scale(0.32)" d="M28.293 149.977C26.5611 149.977 24.8292 149.83 23.1303 149.505C19.0068 148.723 15.1142 146.949 11.733 144.523C8.35171 142.098 5.3663 138.891 3.28805 135.228C2.80973 134.398 2.39738 133.535 2.01802 132.655C1.42423 131.239 0.962403 129.791 0.632525 128.293C0.550053 127.87 0.467583 127.446 0.385113 127.007L0.302643 126.567C0.236668 126.176 0.187186 125.721 0.137704 125.248C0.0882215 124.744 0.0552337 124.207 0.0387397 123.719V123.328C0.00575178 122.856 -0.0107422 122.465 -0.0107422 122.09C-0.0107422 121.521 0.0882215 119.111 0.137704 118.753C0.137704 118.753 0.220173 117.907 0.269656 117.614L0.418101 116.523C0.418101 116.523 0.583041 115.53 0.583041 115.497C0.583041 115.497 1.22631 112.323 1.30878 112.03C1.82009 115.188 2.79323 117.858 4.21171 119.99C6.35593 123.067 9.48976 125.086 13.1844 125.867C16.3843 126.535 19.7325 126.29 22.9159 125.607C28.9197 124.304 34.1813 121.407 39.6243 118.737C42.4778 117.337 45.2652 115.823 48.0362 114.293C56.0688 109.914 63.9858 105.307 71.8533 100.651C78.6653 96.6295 85.6588 92.7716 92.2568 88.4247L93.1469 87.8712L93.7905 87.4968L93.8236 87.4646C94.1041 87.3016 94.3845 87.1224 94.665 86.9433L95.7204 86.3086L95.803 86.2113C101.576 82.5319 106.573 78.446 110.697 74.0179C115.315 69.0524 118.927 63.583 121.418 57.7385C123.81 52.1873 125.195 46.2779 125.558 40.1406L134.118 55.2804L136.131 58.7479L152.195 87.0084L153.037 88.5065C154.439 90.997 157.985 97.4111 161.185 103.825C159.997 103.37 158.744 102.978 157.391 102.621C156.93 102.474 156.468 102.36 155.99 102.246C155.263 102.083 154.554 101.92 153.795 101.79L152.74 101.595C151.866 101.449 150.926 101.318 149.986 101.204L149.771 101.172H149.557C149.293 101.123 149.012 101.09 148.715 101.074C148.303 101.025 147.891 101.009 147.479 100.976C146.192 100.895 145.021 100.862 143.8 100.862C138.308 100.862 132.42 101.644 126.317 103.174C117.888 105.323 108.916 108.937 99.5965 113.967L99.1345 114.114L98.9367 114.293L98.8704 114.325L98.8209 114.374C94.5986 116.881 90.36 119.388 86.1371 121.895C82.1621 124.255 78.187 126.6 74.212 128.944C70.6 131.077 66.9712 133.226 63.3429 135.358C60.1758 137.23 57.009 139.086 53.8421 140.942C50.3783 142.977 46.9476 145.061 43.2365 146.64C41.3067 147.47 39.3439 148.17 37.3152 148.723C34.3627 149.521 31.2948 149.993 28.227 149.977H28.293Z"/>
    <text x="1050" y="348" text-anchor="middle" fill="#FF216B" font-size="11.5" font-weight="600">Abstract Platform</text>
    <text x="1050" y="364" text-anchor="middle" fill="#8b8f98" font-size="10">normalised to ACS</text>
  </g>

  <!-- Badges -->
  <rect x="50" y="145" width="290" height="26" rx="13" fill="#060608" stroke="#F5C61E" stroke-width="1"/>
  <text class="mono" x="195" y="162" text-anchor="middle" fill="#F5C61E" font-size="10">NOT captured by organization-level sinks</text>

  <rect x="50" y="625" width="370" height="26" rx="13" fill="#060608" stroke="#01e69d" stroke-width="1"/>
  <text class="mono" x="235" y="642" text-anchor="middle" fill="#01e69d" font-size="10">requires roles/logging.configWriter on billing account</text>
"""
    ba_svg = generate_svg(ba_title, 1200, 720, ba_drawio, ba_svg_body)

    # 2. Network Threats SVG body
    nt_svg_body = """
  <!-- Banner -->
  <text class="lbl" x="40" y="48" font-size="22" font-weight="700" fill="#FF216B">GCP Network Threat Telemetry to Abstract Security</text>
  <line x1="40" y1="62" x2="420" y2="62" stroke="#FF216B" stroke-width="2"/>

  <!-- Containers -->
  <rect x="40" y="90" width="560" height="610" rx="12" fill="none" stroke="#2e9bf0" stroke-width="1.5" opacity=".6"/>
  <text class="lbl" x="64" y="122" font-size="14" font-weight="600" fill="#2e9bf0">Your GCP Organization / VPC Perimeter</text>

  <rect x="640" y="90" width="380" height="610" rx="12" fill="none" stroke="#01e69d" stroke-width="1.5" opacity=".6"/>
  <text class="lbl" x="664" y="122" font-size="14" font-weight="600" fill="#01e69d">Dedicated logging project</text>

  <rect x="1060" y="90" width="200" height="610" rx="12" fill="none" stroke="#FF216B" stroke-width="1.5" opacity=".6"/>
  <text class="lbl" x="1084" y="122" font-size="14" font-weight="600" fill="#FF216B">Abstract Security</text>

  <!-- Wires -->
  <path d="M168,190 H320 Q360,190 360,230 V310 Q360,340 430,340" class="wire" stroke="#2E9BF0"/>
  <path d="M168,310 H430" class="wire" stroke="#FF216B"/>
  <path d="M168,430 H320 Q360,430 360,390 V360 Q360,340 430,340" class="wire" stroke="#F5C61E"/>
  <path d="M168,550 H320 Q360,550 360,460 V370 Q360,340 430,340" class="wire" stroke="#01e69d"/>
  <path d="M508,340 H680" class="wire" stroke="#FF216B"/>
  <path d="M758,340 H850" class="wire" stroke="#FF216B"/>
  <path d="M928,340 H1100" class="wire" stroke="#FF216B"/>
  <path d="M810,510 V380" class="wire" stroke="#01e69d" stroke-dasharray="6 4"/>

  <!-- Nodes in Org -->
  <g class="lbl">
    <rect class="box" x="90" y="150" width="78" height="78" stroke="#2E9BF0"/>
    <text x="129" y="195" text-anchor="middle" fill="#FFFFFF" font-size="24">🛡️</text>
    <text x="129" y="248" text-anchor="middle" fill="#e9ecf1" font-size="11" font-weight="600">Cloud Armor</text>
    <text x="129" y="264" text-anchor="middle" fill="#8b8f98" font-size="9.5">OWASP &amp; DDoS</text>

    <rect class="box" x="90" y="270" width="78" height="78" stroke="#FF216B"/>
    <text x="129" y="315" text-anchor="middle" fill="#FFFFFF" font-size="24">🚨</text>
    <text x="129" y="368" text-anchor="middle" fill="#e9ecf1" font-size="11" font-weight="600">Cloud IDS</text>
    <text x="129" y="384" text-anchor="middle" fill="#8b8f98" font-size="9.5">Snort Threat Events</text>

    <rect class="box" x="90" y="390" width="78" height="78" stroke="#F5C61E"/>
    <text x="129" y="435" text-anchor="middle" fill="#FFFFFF" font-size="24">🌐</text>
    <text x="129" y="488" text-anchor="middle" fill="#e9ecf1" font-size="11" font-weight="600">DNS Queries</text>
    <text x="129" y="504" text-anchor="middle" fill="#8b8f98" font-size="9.5">DGA &amp; Exfil Lookups</text>

    <rect class="box" x="90" y="510" width="78" height="78" stroke="#01e69d"/>
    <text x="129" y="555" text-anchor="middle" fill="#FFFFFF" font-size="24">🧱</text>
    <text x="129" y="608" text-anchor="middle" fill="#e9ecf1" font-size="11" font-weight="600">VPC Firewall</text>
    <text x="129" y="624" text-anchor="middle" fill="#8b8f98" font-size="9.5">L3/L4 Rule Decisions</text>

    <rect class="box" x="430" y="300" width="78" height="78" stroke="#2E9BF0"/>
    <text x="469" y="345" text-anchor="middle" fill="#FFFFFF" font-size="24">🔀</text>
    <text x="469" y="398" text-anchor="middle" fill="#e9ecf1" font-size="11" font-weight="600">Log Router</text>
    <text x="469" y="414" text-anchor="middle" fill="#8b8f98" font-size="9.5">Network Sink</text>
  </g>

  <!-- Nodes in Logging Project -->
  <g class="lbl">
    <rect class="box" x="680" y="300" width="78" height="78" stroke="#FF216B"/>
    <text x="719" y="345" text-anchor="middle" fill="#FFFFFF" font-size="24">📨</text>
    <text x="719" y="398" text-anchor="middle" fill="#e9ecf1" font-size="11" font-weight="600">Pub/Sub Topic</text>
    <text x="719" y="414" text-anchor="middle" fill="#8b8f98" font-size="9.5">abstract-threats</text>

    <rect class="box" x="850" y="300" width="78" height="78" stroke="#FF216B"/>
    <text x="889" y="345" text-anchor="middle" fill="#FFFFFF" font-size="24">📥</text>
    <text x="889" y="398" text-anchor="middle" fill="#e9ecf1" font-size="11" font-weight="600">Pull Subscription</text>
    <text x="889" y="414" text-anchor="middle" fill="#8b8f98" font-size="9.5">never expires</text>

    <rect class="box" x="770" y="510" width="80" height="78" stroke="#01e69d"/>
    <text x="810" y="555" text-anchor="middle" fill="#FFFFFF" font-size="24">🔑</text>
    <text x="810" y="608" text-anchor="middle" fill="#e9ecf1" font-size="11" font-weight="600">Service Account</text>
    <text x="810" y="624" text-anchor="middle" fill="#01e69d" font-size="9.5">roles/pubsub.subscriber</text>
  </g>

  <!-- Node in Abstract -->
  <g class="lbl">
    <rect class="box" x="1100" y="300" width="80" height="78" stroke="#FF216B"/>
    <text x="1140" y="345" text-anchor="middle" fill="#FFFFFF" font-size="24">⚡</text>
    <text x="1140" y="398" text-anchor="middle" fill="#FF216B" font-size="11" font-weight="600">Abstract SIEM</text>
    <text x="1140" y="414" text-anchor="middle" fill="#8b8f98" font-size="9.5">ECS Network Schema</text>
  </g>

  <!-- Badges -->
  <rect x="50" y="650" width="340" height="26" rx="13" fill="#060608" stroke="#2e9bf0" stroke-width="1"/>
  <text class="mono" x="220" y="667" text-anchor="middle" fill="#2e9bf0" font-size="10">--include-children · covers every project perimeter</text>

  <rect x="640" y="650" width="450" height="26" rx="13" fill="#060608" stroke="#01e69d" stroke-width="1"/>
  <text class="mono" x="865" y="667" text-anchor="middle" fill="#01e69d" font-size="10">normalized to ACS: source.ip, dest.ip, threat.indicator</text>
"""
    nt_svg = generate_svg(nt_title, 1300, 740, nt_drawio, nt_svg_body)

    # 3. Identity and Auth SVG body
    id_svg_body = """
  <!-- Banner -->
  <text class="lbl" x="40" y="48" font-size="22" font-weight="700" fill="#FF216B">GCP &amp; Workspace Identity Authentication Auditing Architecture</text>
  <line x1="40" y1="62" x2="520" y2="62" stroke="#FF216B" stroke-width="2"/>

  <!-- Containers -->
  <rect x="40" y="90" width="380" height="660" rx="12" fill="none" stroke="#2e9bf0" stroke-width="1.5" opacity=".6"/>
  <text class="lbl" x="64" y="122" font-size="14" font-weight="600" fill="#2e9bf0">5 Identity &amp; Authentication Streams</text>

  <rect x="460" y="90" width="460" height="660" rx="12" fill="none" stroke="#01e69d" stroke-width="1.5" opacity=".6"/>
  <text class="lbl" x="484" y="122" font-size="14" font-weight="600" fill="#01e69d">GCP Aggregation &amp; Dedicated Pipeline</text>

  <rect x="960" y="90" width="400" height="420" rx="12" fill="none" stroke="#FF216B" stroke-width="1.5" opacity=".6"/>
  <text class="lbl" x="984" y="122" font-size="14" font-weight="600" fill="#FF216B">Abstract Security SIEM</text>

  <rect x="960" y="530" width="400" height="220" rx="12" fill="none" stroke="#F5C61E" stroke-width="1.5" opacity=".6"/>
  <text class="lbl" x="984" y="562" font-size="14" font-weight="600" fill="#F5C61E">OneUptime Zero-Silent-Failure Monitoring</text>

  <!-- Wires -->
  <path d="M158,180 H500" class="wire" stroke="#2E9BF0"/>
  <path d="M540,220 V380" class="wire" stroke="#2E9BF0"/>
  <path d="M158,300 H500" class="wire" stroke="#7D7589"/>
  <path d="M158,420 H500" class="wire" stroke="#7D7589"/>
  <path d="M158,540 H500" class="wire" stroke="#7D7589"/>
  <path d="M158,660 H500" class="wire" stroke="#7D7589"/>
  <path d="M578,420 H740" class="wire" stroke="#FF216B"/>
  <path d="M780,460 V530" class="wire" stroke="#FF216B"/>
  <path d="M820,570 H1080" class="wire" stroke="#FF216B"/>
  <path d="M1120,290 V340" class="wire" stroke="#FF216B"/>
  <path d="M820,570 H1020" class="wire" stroke="#F5C61E" stroke-dasharray="6 4"/>
  <path d="M1100,640 H1200" class="wire" stroke="#F5C61E"/>

  <!-- Nodes in Identity Streams -->
  <g class="lbl">
    <rect class="box" x="80" y="150" width="78" height="60" stroke="#2E9BF0"/>
    <text x="119" y="185" text-anchor="middle" fill="#FFFFFF" font-size="18">👤</text>
    <text x="119" y="230" text-anchor="middle" fill="#e9ecf1" font-size="11" font-weight="600">User Logins</text>
    <text x="119" y="244" text-anchor="middle" fill="#8b8f98" font-size="9.5">login.googleapis.com</text>

    <rect class="box" x="80" y="270" width="78" height="60" stroke="#7D7589"/>
    <text x="119" y="305" text-anchor="middle" fill="#FFFFFF" font-size="18">🎭</text>
    <text x="119" y="350" text-anchor="middle" fill="#e9ecf1" font-size="11" font-weight="600">Impersonation</text>
    <text x="119" y="364" text-anchor="middle" fill="#8b8f98" font-size="9.5">iamcredentials</text>

    <rect class="box" x="80" y="390" width="78" height="60" stroke="#7D7589"/>
    <text x="119" y="425" text-anchor="middle" fill="#FFFFFF" font-size="18">🔗</text>
    <text x="119" y="470" text-anchor="middle" fill="#e9ecf1" font-size="11" font-weight="600">Workload Identity</text>
    <text x="119" y="484" text-anchor="middle" fill="#8b8f98" font-size="9.5">sts.googleapis.com</text>

    <rect class="box" x="80" y="510" width="78" height="60" stroke="#7D7589"/>
    <text x="119" y="545" text-anchor="middle" fill="#FFFFFF" font-size="18">🗝️</text>
    <text x="119" y="590" text-anchor="middle" fill="#e9ecf1" font-size="11" font-weight="600">Static SA Keys</text>
    <text x="119" y="604" text-anchor="middle" fill="#8b8f98" font-size="9.5">serviceAccountKeyName</text>

    <rect class="box" x="80" y="630" width="78" height="60" stroke="#7D7589"/>
    <text x="119" y="665" text-anchor="middle" fill="#FFFFFF" font-size="18">📋</text>
    <text x="119" y="710" text-anchor="middle" fill="#e9ecf1" font-size="11" font-weight="600">IAM Policy</text>
    <text x="119" y="724" text-anchor="middle" fill="#8b8f98" font-size="9.5">SetIamPolicy / Policy</text>
  </g>

  <!-- Nodes in Pipeline -->
  <g class="lbl">
    <rect class="box" x="500" y="150" width="78" height="70" stroke="#2E9BF0"/>
    <text x="539" y="190" text-anchor="middle" fill="#FFFFFF" font-size="20">☁️</text>
    <text x="539" y="240" text-anchor="middle" fill="#e9ecf1" font-size="10.5" font-weight="600">Workspace Audit</text>
    <text x="539" y="254" text-anchor="middle" fill="#8b8f98" font-size="9">native sharing</text>

    <rect class="box" x="500" y="380" width="78" height="78" stroke="#01e69d"/>
    <text x="539" y="425" text-anchor="middle" fill="#FFFFFF" font-size="24">🔀</text>
    <text x="539" y="478" text-anchor="middle" fill="#e9ecf1" font-size="11" font-weight="600">Log Router</text>
    <text x="539" y="494" text-anchor="middle" fill="#8b8f98" font-size="9.5">Org Aggregated Sink</text>

    <rect class="box" x="740" y="380" width="78" height="78" stroke="#FF216B"/>
    <text x="779" y="425" text-anchor="middle" fill="#FFFFFF" font-size="24">📨</text>
    <text x="779" y="478" text-anchor="middle" fill="#e9ecf1" font-size="11" font-weight="600">Pub/Sub Topic</text>
    <text x="779" y="494" text-anchor="middle" fill="#8b8f98" font-size="9.5">abstract-audit-logs</text>

    <rect class="box" x="740" y="530" width="78" height="78" stroke="#FF216B"/>
    <text x="779" y="575" text-anchor="middle" fill="#FFFFFF" font-size="24">📥</text>
    <text x="779" y="628" text-anchor="middle" fill="#e9ecf1" font-size="11" font-weight="600">Subscription</text>
    <text x="779" y="644" text-anchor="middle" fill="#8b8f98" font-size="9.5">expiration: never</text>
  </g>

  <!-- Nodes in Abstract SIEM -->
  <g class="lbl">
    <rect class="box" x="1080" y="210" width="80" height="78" stroke="#FF216B"/>
    <text x="1120" y="255" text-anchor="middle" fill="#FFFFFF" font-size="24">⚡</text>
    <text x="1120" y="308" text-anchor="middle" fill="#FF216B" font-size="11.5" font-weight="600">SIEM Engine</text>
    <text x="1120" y="324" text-anchor="middle" fill="#8b8f98" font-size="9.5">ECS Identity Normalization</text>

    <rect class="box" x="1080" y="340" width="80" height="78" stroke="#FF216B"/>
    <text x="1120" y="385" text-anchor="middle" fill="#FFFFFF" font-size="24">🎯</text>
    <text x="1120" y="438" text-anchor="middle" fill="#e9ecf1" font-size="11.5" font-weight="600">6 SIEM Rules</text>
    <text x="1120" y="454" text-anchor="middle" fill="#8b8f98" font-size="9.5">Brute Force / Key Leak / Geo</text>
  </g>

  <!-- Nodes in OneUptime -->
  <g class="lbl">
    <rect class="box" x="1020" y="600" width="80" height="78" stroke="#F5C61E"/>
    <text x="1060" y="645" text-anchor="middle" fill="#FFFFFF" font-size="24">🔍</text>
    <text x="1060" y="698" text-anchor="middle" fill="#F5C61E" font-size="11" font-weight="600">Canary Probe</text>
    <text x="1060" y="714" text-anchor="middle" fill="#8b8f98" font-size="9.5">backlog &amp; lag</text>

    <rect class="box" x="1200" y="600" width="80" height="78" stroke="#F5C61E"/>
    <text x="1240" y="645" text-anchor="middle" fill="#FFFFFF" font-size="24">📟</text>
    <text x="1240" y="698" text-anchor="middle" fill="#F5C61E" font-size="11" font-weight="600">Zero Silent Fail</text>
    <text x="1240" y="714" text-anchor="middle" fill="#8b8f98" font-size="9.5">Instant Oncall Alert</text>
  </g>

  <!-- Badges -->
  <rect x="40" y="760" width="460" height="26" rx="13" fill="#060608" stroke="#2e9bf0" stroke-width="1"/>
  <text class="mono" x="270" y="777" text-anchor="middle" fill="#2e9bf0" font-size="10">Dual Ingestion: Native Org Cloud Audit (zero polling) + Reports API</text>

  <rect x="540" y="760" width="480" height="26" rx="13" fill="#060608" stroke="#F5C61E" stroke-width="1"/>
  <text class="mono" x="780" y="777" text-anchor="middle" fill="#F5C61E" font-size="10">Zero-Silent-Failure: synthetic probes guarantee telemetry integrity</text>
"""
    id_svg = generate_svg(id_title, 1400, 800, id_drawio, id_svg_body)

    # =========================================================================
    # 4. ANIMATED TELEMETRY: NETWORK THREATS ANIMATED SVG
    # =========================================================================
    nt_anim_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 480" width="1200" height="480" role="img"
     aria-label="GCP Network Threat Detection telemetry flow into Abstract Security: Cloud Armor, Cloud IDS, DNS queries, and Firewall logs stream through Log Router to Pub/Sub and Abstract.">
  <title>GCP Network Threat Detection telemetry to Abstract Security</title>
  <defs>
    <linearGradient id="pink" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#FF216B"/><stop offset="100%" stop-color="#C2004C"/>
    </linearGradient>
    <linearGradient id="teal" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#01e69d"/><stop offset="100%" stop-color="#008445"/>
    </linearGradient>
    <linearGradient id="amber" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#F5C61E"/><stop offset="100%" stop-color="#D97706"/>
    </linearGradient>
    <linearGradient id="blue" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#2E9BF0"/><stop offset="100%" stop-color="#1D4ED8"/>
    </linearGradient>
    <filter id="glow" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="4" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <path id="p_waf" d="M232,100 H390 Q430,100 430,170 V220"/>
    <path id="p_ids" d="M232,190 H430"/>
    <path id="p_dns" d="M232,280 H430"/>
    <path id="p_fw"  d="M232,370 H390 Q430,370 430,300 V260"/>
    <path id="p_pipe" d="M530,235 H700"/>
    <path id="p_sub" d="M828,235 H980"/>
    <style>
      .lbl{font-family:Barlow,'Barlow Semi Condensed',-apple-system,sans-serif}
      .h{font-size:17px;font-weight:600;letter-spacing:.3px}
      .s{font-size:12.5px;fill:#8b8f98}
      .k{font-size:11px;fill:#f5c61e;font-family:'JetBrains Mono',monospace}
      .wire{stroke:#2a2d35;stroke-width:2;fill:none}
      .box{fill:#0d0f14;stroke:#1e2129;stroke-width:1.5;rx:10}
      @media (prefers-reduced-motion:reduce){.pk{display:none}}
    </style>
  </defs>

  <rect width="1200" height="480" fill="#060608"/>

  <!-- Containers -->
  <rect x="24" y="36" width="536" height="400" rx="14" fill="none" stroke="#2e9bf0" stroke-width="1.5" opacity=".55"/>
  <text class="lbl h" x="44" y="66" fill="#2e9bf0">GCP Organization / VPC Perimeter</text>
  <text class="lbl s" x="44" y="84">Cloud Armor · Cloud IDS · VPC DNS · Firewall Rules</text>

  <rect x="596" y="145" width="292" height="180" rx="14" fill="none" stroke="#01e69d" stroke-width="1.5" opacity=".55"/>
  <text class="lbl h" x="616" y="175" fill="#01e69d">Dedicated logging project</text>
  <text class="lbl s" x="616" y="193">high-volume threat telemetry</text>

  <rect x="944" y="36" width="232" height="400" rx="14" fill="none" stroke="#FF216B" stroke-width="1.5" opacity=".7"/>
  <text class="lbl h" x="964" y="66" fill="#FF216B">Abstract Security SIEM</text>
  <text class="lbl s" x="964" y="84">real-time correlation &amp; detection</text>

  <!-- Wires -->
  <use href="#p_waf" class="wire"/><use href="#p_ids" class="wire"/>
  <use href="#p_dns" class="wire"/><use href="#p_fw" class="wire"/>
  <use href="#p_pipe" class="wire"/><use href="#p_sub" class="wire"/>

  <!-- Sources -->
  <g class="lbl">
    <rect class="box" x="60" y="76" width="172" height="48"/>
    <text x="76" y="97" fill="#2E9BF0" font-size="13.5" font-weight="600">Cloud Armor WAF</text>
    <text x="76" y="114" class="s">OWASP CRS · DDoS blocks</text>

    <rect class="box" x="60" y="166" width="172" height="48"/>
    <text x="76" y="187" fill="#FF216B" font-size="13.5" font-weight="600">Cloud IDS</text>
    <text x="76" y="204" class="s">Snort exploits · malware C2</text>

    <rect class="box" x="60" y="256" width="172" height="48"/>
    <text x="76" y="277" fill="#F5C61E" font-size="13.5" font-weight="600">VPC DNS Queries</text>
    <text x="76" y="294" class="s">DGA lookups · tunneling</text>

    <rect class="box" x="60" y="346" width="172" height="48"/>
    <text x="76" y="367" fill="#01e69d" font-size="13.5" font-weight="600">VPC Firewall Rules</text>
    <text x="76" y="384" class="s">L3/L4 ingress denies</text>
  </g>

  <!-- Log Router -->
  <g class="lbl">
    <rect class="box" x="430" y="207" width="100" height="56" stroke="#2e9bf0"/>
    <text x="480" y="231" text-anchor="middle" fill="#e9ecf1" font-size="13">Log Router</text>
    <text x="480" y="248" text-anchor="middle" class="s">threat sink</text>
  </g>

  <!-- Topic + Sub -->
  <g class="lbl">
    <rect class="box" x="700" y="207" width="128" height="56" stroke="#01e69d"/>
    <text x="764" y="231" text-anchor="middle" fill="#e9ecf1" font-size="13">Pub/Sub topic</text>
    <text x="764" y="248" text-anchor="middle" class="s">network-threats</text>

    <rect class="box" x="980" y="207" width="156" height="56" stroke="#FF216B"/>
    <text x="1058" y="231" text-anchor="middle" fill="#e9ecf1" font-size="13">Pull subscription</text>
    <text x="1058" y="248" text-anchor="middle" class="s">never expires</text>

    <rect class="box" x="980" y="300" width="156" height="70" stroke="#FF216B"/>
    <text x="1058" y="328" text-anchor="middle" fill="#FF216B" font-size="13" font-weight="600">Abstract SIEM</text>
    <text x="1058" y="348" text-anchor="middle" class="s">ECS network schema</text>
  </g>

  <!-- Legend & Badges -->
  <text class="lbl k" x="700" y="291" text-anchor="middle">writer identity has roles/pubsub.publisher</text>
  <text class="lbl k" x="24" y="456" fill="#8b8f98">--include-children · scope is perimeter-wide, covers all current and future subnets</text>

  <!-- Animated Packets -->
  <g class="pk" filter="url(#glow)">
    <!-- WAF packet -->
    <circle r="5" fill="url(#blue)"><animateMotion dur="2.8s" repeatCount="indefinite" begin="0s"><mpath href="#p_waf"/></animateMotion></circle>
    <!-- IDS packet -->
    <circle r="5" fill="url(#pink)"><animateMotion dur="2.4s" repeatCount="indefinite" begin="0.5s"><mpath href="#p_ids"/></animateMotion></circle>
    <!-- DNS packet -->
    <circle r="5" fill="url(#amber)"><animateMotion dur="2.6s" repeatCount="indefinite" begin="1.2s"><mpath href="#p_dns"/></animateMotion></circle>
    <!-- Firewall packet -->
    <circle r="5" fill="url(#teal)"><animateMotion dur="3.0s" repeatCount="indefinite" begin="1.8s"><mpath href="#p_fw"/></animateMotion></circle>

    <!-- Pipeline trunk packets -->
    <circle r="5.5" fill="url(#pink)"><animateMotion dur="1.5s" repeatCount="indefinite" begin="0.7s"><mpath href="#p_pipe"/></animateMotion></circle>
    <circle r="5.5" fill="url(#pink)"><animateMotion dur="1.5s" repeatCount="indefinite" begin="1.4s"><mpath href="#p_pipe"/></animateMotion></circle>

    <!-- Ingestion to Abstract -->
    <circle r="6" fill="url(#pink)"><animateMotion dur="1.6s" repeatCount="indefinite" begin="0.9s"><mpath href="#p_sub"/></animateMotion></circle>
    <circle r="6" fill="url(#pink)"><animateMotion dur="1.6s" repeatCount="indefinite" begin="1.7s"><mpath href="#p_sub"/></animateMotion></circle>
  </g>
</svg>
"""

    # =========================================================================
    # WRITE ASSETS TO DISK
    # =========================================================================
    diagrams_dir = ROOT / "diagrams"
    images_dir = ROOT / "images/diagrams"

    # Write 10-billing-account
    (diagrams_dir / "10-billing-account.drawio").write_text(ba_drawio, encoding="utf-8")
    (diagrams_dir / "10-billing-account.svg").write_text(ba_svg, encoding="utf-8")
    (diagrams_dir / "10-billing-account.spec.json").write_text(json.dumps(ba_spec, indent=1), encoding="utf-8")

    (images_dir / "gcp.billing-account.drawio").write_text(ba_drawio, encoding="utf-8")
    (images_dir / "gcp.billing-account.svg").write_text(ba_svg, encoding="utf-8")
    (images_dir / "gcp.billing-account.spec.json").write_text(json.dumps(ba_spec, indent=1), encoding="utf-8")

    # Write 11-network-threats
    (diagrams_dir / "11-network-threats.drawio").write_text(nt_drawio, encoding="utf-8")
    (diagrams_dir / "11-network-threats.svg").write_text(nt_svg, encoding="utf-8")
    (diagrams_dir / "11-network-threats.spec.json").write_text(json.dumps(nt_spec, indent=1), encoding="utf-8")

    (images_dir / "gcp.network-threats.drawio").write_text(nt_drawio, encoding="utf-8")
    (images_dir / "gcp.network-threats.svg").write_text(nt_svg, encoding="utf-8")
    (images_dir / "gcp.network-threats.spec.json").write_text(json.dumps(nt_spec, indent=1), encoding="utf-8")

    # Write 04-identity-auth-oneuptime
    (diagrams_dir / "04-identity-auth-oneuptime.drawio").write_text(id_drawio, encoding="utf-8")
    (diagrams_dir / "04-identity-auth-oneuptime.svg").write_text(id_svg, encoding="utf-8")
    (diagrams_dir / "04-identity-auth-oneuptime.spec.json").write_text(json.dumps(id_spec, indent=1), encoding="utf-8")

    (images_dir / "gcp.identity-auth-oneuptime.drawio").write_text(id_drawio, encoding="utf-8")
    (images_dir / "gcp.identity-auth-oneuptime.svg").write_text(id_svg, encoding="utf-8")
    (images_dir / "gcp.identity-auth-oneuptime.spec.json").write_text(json.dumps(id_spec, indent=1), encoding="utf-8")

    # Write animated SVGs
    (diagrams_dir / "network-threats-animated.svg").write_text(nt_anim_svg, encoding="utf-8")

    print("Successfully generated all Draw.io, SVG, and spec.json assets!")

if __name__ == "__main__":
    main()
