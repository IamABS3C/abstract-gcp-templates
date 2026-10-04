#!/usr/bin/env python3
"""Build Super High-Resolution, Explanatory, Animated & Branded Diagram Assets
for Google Cloud & Abstract Security Integration Architecture.

Features:
  - Multi-stop Abstract brand gradients (#FF216B -> #E8005D -> #C2004C)
  - Atmospheric dark cyberpunk styling (#060608 with fine cyber-grid & ambient glows)
  - Glowing multi-color animated telemetry packet trains (SVG animateMotion + feGaussianBlur)
  - Comprehensive Legends, Flow Keymaps, IAM requirement callouts, and Live Metrics
  - Dual delivery:
      1. Canonical Draw.io XML (.drawio) with mxGraphModel, Google Cloud stencils,
         AWS group containers, and embedded Abstract SVG logos.
      2. High-resolution standalone vector SVGs with embedded Draw.io metadata.
"""

import json
import os
import pathlib
from xml.sax.saxutils import escape

ROOT = pathlib.Path(__file__).resolve().parent.parent

ABM_B64 = (
    "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxNjguOTQ4IDE0OS45ODEiIHJvbGU9ImltZyIgYXJpYS1sYWJlbD0iQWJzdHJhY3QiPgo8ZGVmcz48bGluZWFyR3JhZGllbnQgaWQ9ImFibS1ncmFkIiB4MT0iNjYuMDQxNyIgeTE9IjkuMDY3NCIgeDI9IjExMi45OTIiIHkyPSI1OC40NTkxIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHN0b3Agc3RvcC1jb2xvcj0iI0ZGMjE2QiIvPjxzdG9wIG9mZnNldD0iMC42NzE3MDIiIHN0b3AtY29sb3I9IiNFODAwNUQiLz48L2xpbmVhckdyYWRpZW50PjwvZGVmcz4KPHBhdGggZmlsbD0iI0U4MDA1RCIgZD0iTTE1My4yNjggMTQ2LjYyNUwxMzMuMjI4IDEwOS42MjJDMTQyLjI1IDEwNy45NzggMTUyLjY0MSAxMDcuODY0IDE2MC45NzEgMTEyLjEyOUMxNjMuMTY0IDExMy4yNTIgMTY1LjIyNiAxMTQuNzE3IDE2Ni41OTUgMTE2LjczNkMxNzEuMDY1IDEyMy4yOTcgMTY4LjUyNSAxMzQuMzY3IDE2NC4wNTUgMTQwLjI2QzE2MS42OCAxNDMuMzg1IDE1OC4zOTcgMTQ2LjIwMSAxNTQuMjkxIDE0OC42MjdDMTU0LjA2IDE0OC4xODggMTUzLjc0NiAxNDcuNTY5IDE1My4yODQgMTQ2LjYyNUgxNTMuMjY4WiIvPgo8cGF0aCBmaWxsPSIjQzIwMDRDIiBkPSJNMTYuNDA5NiAxMTguNDExQzE1LjUzNTQgMTE4LjMxMyAxNC42OTQyIDExOC4wODUgMTMuOTAyNSAxMTcuNjk0QzEyLjA4ODIgMTE2Ljc4MiAxMC43ODUyIDExNS4wNzQgMTAuMDEgMTEzLjIxOEM3LjEwNjk4IDEwNi4yMzMgOS4xNTIyOCA5Ny4yOTYgMTEuNzc0OCA5MC41NTY2QzE0LjI2NTQgODQuMTc1NCAxOC41MDQzIDc4LjM0NzEgMjIuMDE3NiA3Mi40ODY1QzI1LjQzMTkgNjUuNzQ3MSAyOS45MDE3IDU5LjM2NTYgMzMuNzk0MyA1Mi44ODY1QzM1LjkwNTUgNDkuMzUzOSAzOS4wNTU4IDQ2LjYzNTIgNDIuODgyNSA0NS4wMjM2QzQ3LjE3MDkgNDMuMjE2NiA1My43MDI1IDQxLjA4NCA2MC41MTQ1IDQxLjA4NEM2MC41MTQ1IDQxLjA4NCA2MS4wNzUzIDQxLjA4NCA2MS4yMjM3IDQxLjA4NEg2MS41ODY2SDYxLjcxODZINjIuMDQ4NUM2Ni45MzA4IDQxLjI3OTQgNzEuNjE1MSA0Mi40MzUyIDc2LjAxODkgNDQuNTE4OUM3NS40NTggNDQuMjU4NSA2OS4zMjIxIDUyLjI2NzggNjguNzc4MSA1Mi45NTE2QzY1LjQ0NTkgNTcuMDcwMyA2Mi4yOTU5IDYxLjMxOTEgNTkuMjc3NSA2NS42NjU5QzUzLjc4NSA3My41NDQ2IDQ4LjgyMDMgODEuNzY2MSA0NC4yMDIgOTAuMTgyMkM0MS45OTE4IDk0LjIwMzEgMzkuNjQ5NyA5OC4yNTY4IDM3LjY4NjkgMTAyLjM5MkMzNS43MjQxIDEwNi41MjcgMzQuNDM3NSAxMTAuNDAxIDMxLjAwNjggMTEzLjM4QzI4LjU2NTcgMTE1LjQ5NyAyNS40OTc4IDExNi43MzQgMjIuMzgwNSAxMTcuNjQ1QzIwLjQ1MDcgMTE4LjE5OSAxOC4zNzI0IDExOC42MzggMTYuNDA5NiAxMTguNDExWiIvPgo8cGF0aCBmaWxsPSJ1cmwoI2FibS1ncmFkKSIgZD0iTTEwOC40NTggNjQuNjYxQzEwMy45MjIgNTcuNDk4MSA5Ni4yODUyIDQ3LjY0OTEgODUuNDQ4NyA0MC45MDk1TDgzLjA1NzQgMzkuNDc2OUM3Ni41NTg0IDM1LjYzNSA2OS40ODI4IDMzLjU4MzggNjIuMDI3NSAzMy4zNTU5QzYxLjU2NTcgMzMuMzM5NiA2MS4wNzA4IDMzLjMzOTYgNjAuNTkyNSAzMy4zMzk2QzU0LjI0MjMgMzMuMzM5NiA0OC41MDI0IDM0LjYyNTcgNDMuNzg1MiAzNi4yMjExTDQ3LjI2NTQgMzAuNDQxOUw0OC43MTY4IDI4LjA4MTRMNTAuODQ0NiAyNC41MzI1TDUxLjgzNDIgMjIuODg4NEM1NC42MDUyIDE4LjI2NSA1Ny43MDYxIDE0LjIyNzggNjEuMDIxNCAxMC44NTc5TDYxLjM2NzcgMTAuNTE2MUM2Mi4wNjA1IDkuODQ4NjQgNjIuNzM2NSA5LjE5NzQ0IDYzLjQyOTUgOC41OTUxNUM2NC4yMDQ1IDcuOTExNDEgNjUuMDI5NSA3LjI0Mzk3IDY1Ljg4NzEgNi42MDkwOEM2Ni43Nzc5IDUuOTQxNiA2Ny42NTE4IDUuMzM5MjcgNjguNTI2MyA0Ljc4NTc3QzY4Ljg3MjUgNC41NTc4NiA2OS4xNTI5IDQuMzc4NzkgNjkuNDMzNCA0LjI0ODU2TDY5Ljg3ODQgNC4wMjA2NUw2OS45NjExIDMuOTM5MjVDNzAuMTI2MyAzLjg0MTU4IDcwLjI5MSAzLjc0MzkgNzAuNDU2MiAzLjY0NjIyTDcwLjkxNzYgMy40MTgzMkM3MS42NDM3IDMuMDQzODkgNzIuNDE4NyAyLjY2OTQ3IDczLjM3NTIgMi4yNDYyMUw3My41MjM2IDIuMTgxMDlDNzQuNzExMSAxLjcwODk5IDc1Ljc5OTcgMS4zMzQ1NyA3Ni44Mzg4IDEuMDI1MjZMNzcuMDUzNSAwLjk3NjQyM0M3Ny42MzA3IDAuODI5OTEzIDc4LjE1ODQgMC42ODMzOTYgNzguNzM2MiAwLjU4NTcyMkw4MC42OTg3IDAuMjQzODU3QzgxLjgwMzYgMC4wOTczNDM4IDgyLjkwOTEgMC4wMzIyMjY2IDg0LjAxMzkgMC4wMzIyMjY2Qzg1LjAxOTkgMC4wMzIyMjY2IDg2LjA5MjIgMC4wOTczNDM5IDg3LjIxNCAwLjIyNzU3OEM4Ny42MDk2IDAuMjc2NDE2IDg4LjAyMjEgMC4zNDE1MzMgODguNDE3OCAwLjQwNjY1TDg4LjQ1MSAwLjQzOTIwOUw4OS40NDA2IDAuNjAyMDAxQzg5LjYzODUgMC42MzQ1NTkgODkuODM2MyAwLjY4MzM5NiA5MC4wNjczIDAuNzMyMjMzQzkwLjU0NTUgMC44NDYxOSA5MC45NzQzIDAuOTYwMTQ2IDkxLjM3MDYgMS4wOTAzOEw5MS43NjYyIDEuMjA0MzRDOTIuMDYyOSAxLjMwMjAxIDkyLjM3NjUgMS4zODM0MSA5Mi42NzMzIDEuNDk3MzZMOTMuMzE2OCAxLjcyNTI3TDkzLjk1OTcgMS45Njk0NkM5NC4zNTU5IDIuMTMyMjUgOTQuNzg0NyAyLjMxMTMyIDk1LjIxMzUgMi41MDY2OEM5Ni4xMDQzIDIuODk3MzggOTcuMDExNCAzLjM1MzIgOTcuOTM0NyAzLjg5MDQxQzk4LjgyNTUgNC4zOTUwNyA5OS43MTYzIDQuOTQ4NTcgMTAwLjY3MyA1LjU5OTc0QzEwMy4zOTUgNy41MDQ0MyAxMDYuMDUgOS45MTM3MyAxMDguNTQgMTIuNzEzOEMxMDkuODI3IDE0LjE2MjYgMTExLjA5NyAxNS43OTA2IDExMi4zMzQgMTcuNTMyNEMxMTMuNzM2IDE5LjUwMjMgMTE0Ljk1NyAyMS43OTc2IDExNS45OCAyNC4zODZDMTE2LjQwOCAyNS40NDQyIDExNi43MjEgMjYuNTUxMSAxMTYuOTIgMjcuNjc0NEMxMTcuMzMyIDI5LjkzNzIgMTE3LjYxMiAzMS43NjA1IDExNy43MTEgMzIuOTMyNkMxMTcuNzQ0IDMzLjI5MDggMTE3Ljc3NyAzMy42NDg5IDExNy43NzcgMzMuOTkwOFYzNC4xODYxQzExNy44MSAzNC40MzA0IDExNy44MjcgMzQuNjU4MyAxMTcuODI3IDM0LjkxODdWMzUuMDgxNUMxMTcuODU5IDM1LjY4MzggMTE3Ljg3NiAzNi4zMDI0IDExNy44NzYgMzYuOTUzNkMxMTcuODc2IDQyLjc4MTYgMTE2LjgwNCA0OC40MTQzIDExNC42OTIgNTMuNzA1TDExNC42MjcgNTMuODY3OEMxMTQuNTc3IDUzLjk5OCAxMTQuNTI4IDU0LjExMiAxMTQuNDc4IDU0LjIyNTlMMTE0LjM5NiA1NC40MDVMMTE0LjMzIDU0LjU4NDFMMTE0LjI2NCA1NC43MzA2TDExNC4yMTQgNTQuODc3MUMxMTQuMjE0IDU0Ljg3NzEgMTE0LjE0OCA1NS4wMzk5IDExNC4xMTUgNTUuMTIxM0MxMTIuNjQ3IDU4LjQ3NDggMTEwLjc1MSA2MS42ODE4IDEwOC40NDEgNjQuNzI2MUwxMDguNDU4IDY0LjY2MVoiLz4KPHBhdGggZmlsbD0iI0ZGMjE2QiIgZD0iTTI4LjI5MyAxNDkuOTc3QzI2LjU2MTEgMTQ5Ljk3NyAyNC44MjkyIDE0OS44MyAyMy4xMzAzIDE0OS41MDVDMTkuMDA2OCAxNDguNzIzIDE1LjExNDIgMTQ2Ljk0OSAxMS43MzMgMTQ0LjUyM0M4LjM1MTcxIDE0Mi4wOTggNS4zNjYzIDEzOC44OTEgMy4yODgwNSAxMzUuMjI4QzIuODA5NzMgMTM0LjM5OCAyLjM5NzM4IDEzMy41MzUgMi4wMTgwMiAxMzIuNjU1QzEuNDI0MjMgMTMxLjIzOSAwLjk2MjQwMyAxMjkuNzkxIDAuNjMyNTI1IDEyOC4yOTNDMC41NTAwNTMgMTI3Ljg3IDAuNDY3NTgzIDEyNy40NDYgMC4zODUxMTMgMTI3LjAwN0wwLjMwMjY0MyAxMjYuNTY3QzAuMjM2NjY4IDEyNi4xNzYgMC4xODcxODYgMTI1LjcyMSAwLjEzNzcwNCAxMjUuMjQ4QzAuMDg4MjIxNSAxMjQuNzQ0IDAuMDU1MjMzNyAxMjQuMjA3IDAuMDM4NzM5NyAxMjMuNzE5VjEyMy4zMjhDMC4wMDU3NTE3OCAxMjIuODU2IC0wLjAxMDc0MjIgMTIyLjQ2NSAtMC4wMTA3NDIyIDEyMi4wOUMtMC4wMTA3NDIyIDEyMS41MjEgMC4wODgyMjE1IDExOS4xMTEgMC4xMzc3MDQgMTE4Ljc1M0MwLjEzNzcwNCAxMTguNzUzIDAuMjIwMTczIDExNy45MDcgMC4yNjk2NTYgMTE3LjYxNEwwLjQxODEwMSAxMTYuNTIzQzAuNDE4MTAxIDExNi41MjMgMC41ODMwNDEgMTE1LjUzIDAuNTgzMDQxIDExNS40OTdDMC41ODMwNDEgMTE1LjQ5NyAxLjIyNjMxIDExMi4zMjMgMS4zMDg3OCAxMTIuMDNDMS44MjAwOSAxMTUuMTg4IDIuNzkzMjMgMTE3Ljg1OCA0LjIxMTcxIDExOS45OUM2LjM1NTkzIDEyMy4wNjcgOS40ODk3NiAxMjUuMDg2IDEzLjE4NDQgMTI1Ljg2N0MxNi4zODQzIDEyNi41MzUgMTkuNzMyNSAxMjYuMjkgMjIuOTE1OSAxMjUuNjA3QzI4LjkxOTcgMTI0LjMwNCAzNC4xODEzIDEyMS40MDcgMzkuNjI0MyAxMTguNzM3QzQyLjQ3NzggMTE3LjMzNyA0NS4yNjUyIDExNS44MjMgNDguMDM2MiAxMTQuMjkzQzU2LjA2ODggMTA5LjkxNCA2My45ODU4IDEwNS4zMDcgNzEuODUzMyAxMDAuNjUxQzc4LjY2NTMgOTYuNjI5NSA4NS42NTg4IDkyLjc3MTYgOTIuMjU2OCA4OC40MjQ3TDkzLjE0NjkgODcuODcxMkw5My43OTA1IDg3LjQ5NjhMOTMuODIzNiA4Ny40NjQ2Qzk0LjEwNDEgODcuMzAxNiA5NC4zODQ1IDg3LjEyMjQgOTQuNjY1IDg2Ljk0MzNMOTUuNzIwNCA4Ni4zMDg2TDk1LjgwMyA4Ni4yMTEzQzEwMS41NzYgODIuNTMxOSAxMDYuNTczIDc4LjQ0NiAxMTAuNjk3IDc0LjAxNzlDMTE1LjMxNSA2OS4wNTI0IDExOC45MjcgNjMuNTgzIDEyMS40MTggNTcuNzM4NUMxMjMuODEgNTIuMTg3MyAxMjUuMTk1IDQ2LjI3NzkgMTI1LjU1OCA0MC4xNDA2TDEzNC4xMTggNTUuMjgwNEwxMzYuMTMxIDU4Ljc0NzlMMTUyLjE5NSA4Ny4wMDg0TDE1My4wMzcgODguNTA2NUMxNTQuNDM5IDkwLjk5NyAxNTcuOTg1IDk3LjQxMTEgMTYxLjE4NSAxMDMuODI1QzE1OS45OTcgMTAzLjM3IDE1OC43NDQgMTAyLjk3OCAxNTcuMzkxIDEwMi42MjFDMTU2LjkzIDEwMi40NzQgMTU2LjQ2OCAxMDIuMzYgMTU1Ljk5IDEwMi4yNDZDMTU1LjI2MyAxMDIuMDgzIDE1NC41NTQgMTAxLjkyIDE1My43OTUgMTAxLjc5TDE1Mi43NCAxMDEuNTk1QzE1MS44NjYgMTAxLjQ0OSAxNTAuOTI2IDEwMS4zMTggMTQ5Ljk4NiAxMDEuMjA0TDE0OS43NzEgMTAxLjE3MkgxNDkuNTU3QzE0OS4yOTMgMTAxLjEyMyAxNDkuMDEyIDEwMS4wOSAxNDguNzE1IDEwMS4wNzRDMTQ4LjMwMyAxMDEuMDI1IDE0Ny44OTEgMTAxLjAwOSAxNDcuNDc5IDEwMC45NzZDMTQ2LjE5MiAxMDAuODk1IDE0NS4wMjEgMTAwLjg2MiAxNDMuOCAxMDAuODYyQzEzOC4zMDggMTAwLjg2MiAxMzIuNDIgMTAxLjY0NCAxMjYuMzE3IDEwMy4xNzRDMTE3Ljg4OCAxMDUuMzIzIDEwOC45MTYgMTA4LjkzNyA5OS41OTY1IDExMy45NjdMOTkuMTM0NSAxMTQuMTE0TDk4LjkzNjcgMTE0LjI5M0w5OC44NzA0IDExNC4zMjVMOTguODIwOSAxMTQuMzc0Qzk0LjU5ODYgMTE2Ljg4MSA5MC4zNiAxMTkuMzg4IDg2LjEzNzEgMTIxLjg5NUM4Mi4xNjIxIDEyNC4yNTUgNzguMTg3IDEyNi42IDc0LjIxMiAxMjguOTQ0QzcwLjYgMTMxLjA3NyA2Ni45NzEyIDEzMy4yMjYgNjMuMzQyOSAxMzUuMzU4QzYwLjE3NTggMTM3LjIzIDU3LjAwOSAxMzkuMDg2IDUzLjg0MjEgMTQwLjk0MkM1MC4zNzgzIDE0Mi45NzcgNDYuOTQ3NiAxNDUuMDYxIDQzLjIzNjUgMTQ2LjY0QzQxLjMwNjcgMTQ3LjQ3IDM5LjM0MzkgMTQ4LjE3IDM3LjMxNTIgMTQ4LjcyM0MzNC4zNjI3IDE0OS41MjEgMzEuMjk0OCAxNDkuOTkzIDI4LjIyNyAxNDkuOTc3SDI4LjI5M1oiLz4KPC9zdmc+Cg=="
)

def build_drawio_xml(title, width, height, elements):
    cells = "\n".join(elements)
    return (
        f'<mxfile host="app.diagrams.net" type="device">'
        f'<diagram id="{title}" name="{title}">'
        f'<mxGraphModel dx="1400" dy="900" grid="0" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{width}" pageHeight="{height}" background="#060608" math="0" shadow="0">'
        f'<root><mxCell id="0"/><mxCell id="1" parent="0"/>\n{cells}\n'
        f'</root></mxGraphModel></diagram></mxfile>'
    )

def build_vector_svg(title, width, height, drawio_xml, svg_body):
    escaped_xml = escape(drawio_xml, {'"': '&quot;'})
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     version="1.1" width="{width}px" height="{height}px" viewBox="0 0 {width} {height}"
     content="{escaped_xml}"
     style="background: #060608; background-color: light-dark(#060608, #e8e8ea); color-scheme: light dark;">
  <title>{title}</title>
  <defs>
    <!-- Brand Gradients -->
    <linearGradient id="abm-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FF216B"/>
      <stop offset="67%" stop-color="#E8005D"/>
      <stop offset="100%" stop-color="#C2004C"/>
    </linearGradient>
    <linearGradient id="teal-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#01e69d"/>
      <stop offset="100%" stop-color="#008445"/>
    </linearGradient>
    <linearGradient id="blue-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#2E9BF0"/>
      <stop offset="100%" stop-color="#1D4ED8"/>
    </linearGradient>
    <linearGradient id="amber-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#F5C61E"/>
      <stop offset="100%" stop-color="#D97706"/>
    </linearGradient>

    <!-- Ambient Atmospheric Glows -->
    <radialGradient id="glow-ambient-left" cx="20%" cy="30%" r="50%">
      <stop offset="0%" stop-color="#2E9BF0" stop-opacity="0.12"/>
      <stop offset="100%" stop-color="#060608" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glow-ambient-right" cx="85%" cy="35%" r="50%">
      <stop offset="0%" stop-color="#FF216B" stop-opacity="0.15"/>
      <stop offset="100%" stop-color="#060608" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glow-ambient-center" cx="50%" cy="50%" r="45%">
      <stop offset="0%" stop-color="#01e69d" stop-opacity="0.08"/>
      <stop offset="100%" stop-color="#060608" stop-opacity="0"/>
    </radialGradient>

    <!-- Glowing Filters -->
    <filter id="glow-strong" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="4.5" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="glow-subtle" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="2.5" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>

    <!-- Fine Cyber Grid Pattern -->
    <pattern id="cyber-grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#161822" stroke-width="0.8" opacity="0.65"/>
    </pattern>

    <style>
      .lbl {{ font-family: Barlow, 'Barlow Semi Condensed', -apple-system, sans-serif; }}
      .mono {{ font-family: 'JetBrains Mono', ui-monospace, monospace; }}
      .card {{ fill: #0b0d13; stroke-width: 1.5; rx: 10px; }}
      .wire {{ stroke-width: 2.2; fill: none; }}
      .badge-text {{ font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 500; }}
      .key-title {{ font-size: 11px; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase; }}
      .key-desc {{ font-size: 10.5px; fill: #8b8f98; }}
      @media (prefers-reduced-motion: reduce) {{ .pk {{ display: none; }} }}
    </style>
  </defs>

  <!-- Background Base & Cyber Grid -->
  <rect width="100%" height="100%" fill="#060608"/>
  <rect width="100%" height="100%" fill="url(#cyber-grid)"/>
  <rect width="100%" height="100%" fill="url(#glow-ambient-left)"/>
  <rect width="100%" height="100%" fill="url(#glow-ambient-right)"/>
  <rect width="100%" height="100%" fill="url(#glow-ambient-center)"/>

  {svg_body}
</svg>"""

def main():
    print("Building Super High-Res, Explanatory & Branded Diagram Suite...")
    diagrams_dir = ROOT / "diagrams"
    images_dir = ROOT / "images/diagrams"

    # =========================================================================
    # 1. UPGRADE FLOW-ANIMATED.SVG (Org-Wide Audit Log Pipeline)
    # =========================================================================
    flow_animated_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 540" width="1280" height="540" role="img"
     aria-label="GCP organization-wide log telemetry flow into Abstract Security: Every project streams through the Log Router to a Pub/Sub topic in a dedicated logging project, which Abstract pulls from.">
  <title>GCP Organization-Wide Audit Telemetry into Abstract Security</title>
  <defs>
    <linearGradient id="pink" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#FF216B"/><stop offset="100%" stop-color="#C2004C"/>
    </linearGradient>
    <linearGradient id="teal" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#01e69d"/><stop offset="100%" stop-color="#008445"/>
    </linearGradient>
    <linearGradient id="blue" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#2E9BF0"/><stop offset="100%" stop-color="#1D4ED8"/>
    </linearGradient>
    <radialGradient id="glow-ambient-left" cx="20%" cy="30%" r="50%">
      <stop offset="0%" stop-color="#2E9BF0" stop-opacity="0.12"/><stop offset="100%" stop-color="#060608" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glow-ambient-right" cx="85%" cy="35%" r="50%">
      <stop offset="0%" stop-color="#FF216B" stop-opacity="0.15"/><stop offset="100%" stop-color="#060608" stop-opacity="0"/>
    </radialGradient>
    <filter id="glow" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="4.5" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <pattern id="cyber-grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#161822" stroke-width="0.8" opacity="0.65"/>
    </pattern>

    <!-- Packet Motion Paths -->
    <path id="p1" d="M232,138 H390 Q430,138 430,174 V196"/>
    <path id="p2" d="M232,210 H430"/>
    <path id="p3" d="M232,318 H390 Q430,318 430,282 V224"/>
    <path id="p4" d="M530,210 H710"/>
    <path id="p5" d="M838,210 H1010"/>

    <style>
      .lbl{font-family:Barlow,'Barlow Semi Condensed',-apple-system,sans-serif}
      .h{font-size:16px;font-weight:700;letter-spacing:.3px}
      .s{font-size:12px;fill:#8b8f98}
      .k{font-size:11px;fill:#f5c61e;font-family:'JetBrains Mono',monospace}
      .wire{stroke:#2a2d35;stroke-width:2.2;fill:none}
      .box{fill:#0d0f14;stroke:#1e2129;stroke-width:1.5;rx:10}
      .key-title{font-size:11px;font-weight:700;letter-spacing:0.5px;text-transform:uppercase}
      .key-desc{font-size:10.5px;fill:#8b8f98}
      @media (prefers-reduced-motion:reduce){.pk{display:none}}
    </style>
  </defs>

  <rect width="100%" height="100%" fill="#060608"/>
  <rect width="100%" height="100%" fill="url(#cyber-grid)"/>
  <rect width="100%" height="100%" fill="url(#glow-ambient-left)"/>
  <rect width="100%" height="100%" fill="url(#glow-ambient-right)"/>

  <!-- Live Pulse Status Badge -->
  <g class="lbl" transform="translate(1030, 24)">
    <rect x="0" y="0" width="210" height="26" rx="13" fill="#0d0f14" stroke="#01e69d" stroke-width="1.2"/>
    <circle cx="16" cy="13" r="4.5" fill="#01e69d" filter="url(#glow)">
      <animate attributeName="opacity" values="1;0.3;1" dur="2s" repeatCount="indefinite"/>
    </circle>
    <text x="28" y="17" fill="#01e69d" font-size="10.5" font-family="'JetBrains Mono',monospace" font-weight="600">LIVE TELEMETRY STREAM</text>
  </g>

  <!-- Containers -->
  <rect x="24" y="56" width="546" height="340" rx="14" fill="none" stroke="#2e9bf0" stroke-width="1.5" opacity=".6"/>
  <text class="lbl h" x="44" y="86" fill="#2e9bf0">GCP Organization Perimeter</text>
  <text class="lbl s" x="44" y="104">Every workload project — present and future (via --include-children)</text>

  <rect x="606" y="120" width="292" height="210" rx="14" fill="none" stroke="#01e69d" stroke-width="1.5" opacity=".6"/>
  <text class="lbl h" x="626" y="150" fill="#01e69d">Dedicated Logging Project</text>
  <text class="lbl s" x="626" y="168">Isolated security boundary · zero workload access</text>

  <rect x="944" y="56" width="310" height="340" rx="14" fill="none" stroke="#FF216B" stroke-width="1.5" opacity=".7"/>
  <text class="lbl h" x="964" y="86" fill="#FF216B">Abstract Security SIEM</text>
  <text class="lbl s" x="964" y="104">Zero-silent-failure streaming analytics</text>

  <!-- Wires -->
  <use href="#p1" class="wire"/><use href="#p2" class="wire"/><use href="#p3" class="wire"/>
  <use href="#p4" class="wire"/><use href="#p5" class="wire"/>

  <!-- Sources -->
  <g class="lbl">
    <rect class="box" x="60" y="114" width="172" height="48"/>
    <text x="76" y="135" fill="#e9ecf1" font-size="13.5" font-weight="600">Project A (Prod)</text>
    <text x="76" y="152" class="s">IAM · GKE · BigQuery</text>

    <rect class="box" x="60" y="186" width="172" height="48"/>
    <text x="76" y="207" fill="#e9ecf1" font-size="13.5" font-weight="600">Project B (Data)</text>
    <text x="76" y="224" class="s">Storage · KMS · Cloud SQL</text>

    <rect class="box" x="60" y="294" width="172" height="48"/>
    <text x="76" y="315" fill="#01e69d" font-size="13.5" font-weight="600">Project Z (Future)</text>
    <text x="76" y="332" class="s">Automatically captured</text>
  </g>

  <!-- Log Router -->
  <g class="lbl">
    <rect class="box" x="430" y="182" width="100" height="56" stroke="#2e9bf0"/>
    <text x="480" y="206" text-anchor="middle" fill="#e9ecf1" font-size="13" font-weight="600">Log Router</text>
    <text x="480" y="223" text-anchor="middle" class="s">aggregated sink</text>
  </g>

  <!-- Topic + Sub -->
  <g class="lbl">
    <rect class="box" x="710" y="182" width="128" height="56" stroke="#01e69d"/>
    <text x="774" y="206" text-anchor="middle" fill="#e9ecf1" font-size="13" font-weight="600">Pub/Sub topic</text>
    <text x="774" y="223" text-anchor="middle" class="s">7-day retention</text>

    <rect class="box" x="1010" y="182" width="166" height="56" stroke="#FF216B"/>
    <text x="1093" y="206" text-anchor="middle" fill="#e9ecf1" font-size="13" font-weight="600">Pull subscription</text>
    <text x="1093" y="223" text-anchor="middle" class="s">expiration: never</text>

    <!-- Abstract Logo & Label -->
    <rect class="box" x="1010" y="280" width="166" height="88" stroke="#FF216B"/>
    <text x="1093" y="322" text-anchor="middle" fill="#FFFFFF" font-size="28">⚡</text>
    <text x="1093" y="346" text-anchor="middle" fill="#FF216B" font-size="12.5" font-weight="700">Abstract Security</text>
    <text x="1093" y="360" text-anchor="middle" class="s">normalised to ACS</text>
  </g>

  <!-- Architecture Callouts -->
  <text class="lbl k" x="774" y="268" text-anchor="middle">writer identity needs</text>
  <text class="lbl k" x="774" y="283" text-anchor="middle">roles/pubsub.publisher</text>

  <!-- Animated Glowing Packets -->
  <g class="pk" fill="url(#pink)" filter="url(#glow)">
    <circle r="5"><animateMotion dur="3.2s" repeatCount="indefinite" begin="0s"><mpath href="#p1"/></animateMotion></circle>
    <circle r="5"><animateMotion dur="3.2s" repeatCount="indefinite" begin="1.1s"><mpath href="#p2"/></animateMotion></circle>
    <circle r="5"><animateMotion dur="3.2s" repeatCount="indefinite" begin="2.0s"><mpath href="#p3"/></animateMotion></circle>

    <!-- Log Router -> Topic -->
    <circle r="5.5" fill="url(#teal)"><animateMotion dur="1.7s" repeatCount="indefinite" begin="0.7s"><mpath href="#p4"/></animateMotion></circle>
    <circle r="5.5" fill="url(#teal)"><animateMotion dur="1.7s" repeatCount="indefinite" begin="1.5s"><mpath href="#p4"/></animateMotion></circle>

    <!-- Topic -> Pull Subscription -> Abstract -->
    <circle r="6"><animateMotion dur="1.6s" repeatCount="indefinite" begin="0.3s"><mpath href="#p5"/></animateMotion></circle>
    <circle r="6"><animateMotion dur="1.6s" repeatCount="indefinite" begin="1.1s"><mpath href="#p5"/></animateMotion></circle>
  </g>

  <!-- Detailed Legend & Flow Keymap at Bottom -->
  <g class="lbl" transform="translate(24, 420)">
    <rect x="0" y="0" width="1230" height="96" rx="10" fill="#0b0d13" stroke="#1f2330" stroke-width="1.2"/>

    <!-- Key 1 -->
    <g transform="translate(24, 20)">
      <circle cx="10" cy="10" r="10" fill="#2E9BF0"/>
      <text x="10" y="14" text-anchor="middle" fill="#FFFFFF" font-size="11" font-weight="700">1</text>
      <text class="key-title" x="30" y="10" fill="#2E9BF0">Project Emission</text>
      <text class="key-desc" x="30" y="26">Audit logs emitted locally</text>
      <text class="key-desc" x="30" y="40">Covered by containment</text>
    </g>

    <!-- Key 2 -->
    <g transform="translate(260, 20)">
      <circle cx="10" cy="10" r="10" fill="#2E9BF0"/>
      <text x="10" y="14" text-anchor="middle" fill="#FFFFFF" font-size="11" font-weight="700">2</text>
      <text class="key-title" x="30" y="10" fill="#2E9BF0">Aggregated Sink</text>
      <text class="key-desc" x="30" y="26">--include-children enabled</text>
      <text class="key-desc" x="30" y="40">Routes all child projects</text>
    </g>

    <!-- Key 3 -->
    <g transform="translate(500, 20)">
      <circle cx="10" cy="10" r="10" fill="#01e69d"/>
      <text x="10" y="14" text-anchor="middle" fill="#FFFFFF" font-size="11" font-weight="700">3</text>
      <text class="key-title" x="30" y="10" fill="#01e69d">Pub/Sub Transport</text>
      <text class="key-desc" x="30" y="26">Writer identity publisher</text>
      <text class="key-desc" x="30" y="40">7-day durable retention</text>
    </g>

    <!-- Key 4 -->
    <g transform="translate(740, 20)">
      <circle cx="10" cy="10" r="10" fill="#FF216B"/>
      <text x="10" y="14" text-anchor="middle" fill="#FFFFFF" font-size="11" font-weight="700">4</text>
      <text class="key-title" x="30" y="10" fill="#FF216B">Secure Pulling</text>
      <text class="key-desc" x="30" y="26">Subscriber SA least privilege</text>
      <text class="key-desc" x="30" y="40">Subscription never expires</text>
    </g>

    <!-- Key 5 -->
    <g transform="translate(980, 20)">
      <circle cx="10" cy="10" r="10" fill="#FF216B"/>
      <text x="10" y="14" text-anchor="middle" fill="#FFFFFF" font-size="11" font-weight="700">5</text>
      <text class="key-title" x="30" y="10" fill="#FF216B">ACS Normalization</text>
      <text class="key-desc" x="30" y="26">Normalized to Elastic ECS</text>
      <text class="key-desc" x="30" y="40">Zero silent drops</text>
    </g>
  </g>
</svg>"""

    (diagrams_dir / "flow-animated.svg").write_text(flow_animated_svg, encoding="utf-8")

    # =========================================================================
    # 2. UPGRADE NETWORK-THREATS-ANIMATED.SVG
    # =========================================================================
    nt_anim_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 560" width="1280" height="560" role="img"
     aria-label="GCP Network Threat Detection telemetry flow into Abstract Security: Cloud Armor WAF, Cloud IDS, DNS queries, and Firewall logs stream through Log Router to Pub/Sub and Abstract.">
  <title>GCP Network Threat Detection Telemetry into Abstract Security</title>
  <defs>
    <linearGradient id="pink" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#FF216B"/><stop offset="100%" stop-color="#C2004C"/></linearGradient>
    <linearGradient id="teal" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#01e69d"/><stop offset="100%" stop-color="#008445"/></linearGradient>
    <linearGradient id="amber" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#F5C61E"/><stop offset="100%" stop-color="#D97706"/></linearGradient>
    <linearGradient id="blue" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#2E9BF0"/><stop offset="100%" stop-color="#1D4ED8"/></linearGradient>
    <radialGradient id="glow-ambient-left" cx="20%" cy="30%" r="50%">
      <stop offset="0%" stop-color="#2E9BF0" stop-opacity="0.12"/><stop offset="100%" stop-color="#060608" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glow-ambient-right" cx="85%" cy="35%" r="50%">
      <stop offset="0%" stop-color="#FF216B" stop-opacity="0.15"/><stop offset="100%" stop-color="#060608" stop-opacity="0"/>
    </radialGradient>
    <filter id="glow" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="4.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <pattern id="cyber-grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#161822" stroke-width="0.8" opacity="0.65"/>
    </pattern>

    <path id="p_waf" d="M232,100 H390 Q430,100 430,170 V220"/>
    <path id="p_ids" d="M232,185 H430"/>
    <path id="p_dns" d="M232,270 H430"/>
    <path id="p_fw"  d="M232,355 H390 Q430,355 430,290 V245"/>
    <path id="p_pipe" d="M530,230 H710"/>
    <path id="p_sub" d="M838,230 H1010"/>

    <style>
      .lbl{font-family:Barlow,'Barlow Semi Condensed',-apple-system,sans-serif}
      .h{font-size:16px;font-weight:700;letter-spacing:.3px}
      .s{font-size:12px;fill:#8b8f98}
      .k{font-size:11px;fill:#f5c61e;font-family:'JetBrains Mono',monospace}
      .wire{stroke:#2a2d35;stroke-width:2.2;fill:none}
      .box{fill:#0d0f14;stroke:#1e2129;stroke-width:1.5;rx:10}
      .key-title{font-size:11px;font-weight:700;letter-spacing:0.5px;text-transform:uppercase}
      .key-desc{font-size:10.5px;fill:#8b8f98}
      @media (prefers-reduced-motion:reduce){.pk{display:none}}
    </style>
  </defs>

  <rect width="100%" height="100%" fill="#060608"/>
  <rect width="100%" height="100%" fill="url(#cyber-grid)"/>
  <rect width="100%" height="100%" fill="url(#glow-ambient-left)"/>
  <rect width="100%" height="100%" fill="url(#glow-ambient-right)"/>

  <!-- Live Pulse Status Badge -->
  <g class="lbl" transform="translate(1010, 20)">
    <rect x="0" y="0" width="230" height="26" rx="13" fill="#0d0f14" stroke="#FF216B" stroke-width="1.2"/>
    <circle cx="16" cy="13" r="4.5" fill="#FF216B" filter="url(#glow)">
      <animate attributeName="opacity" values="1;0.3;1" dur="1.8s" repeatCount="indefinite"/>
    </circle>
    <text x="28" y="17" fill="#FF216B" font-size="10.5" font-family="'JetBrains Mono',monospace" font-weight="600">HIGH-SIGNAL THREAT STREAM</text>
  </g>

  <!-- Containers -->
  <rect x="24" y="46" width="546" height="370" rx="14" fill="none" stroke="#2e9bf0" stroke-width="1.5" opacity=".6"/>
  <text class="lbl h" x="44" y="74" fill="#2e9bf0">VPC Perimeter &amp; Network Defense</text>
  <text class="lbl s" x="44" y="92">L3/L4/L7 threat events across all projects</text>

  <rect x="606" y="140" width="292" height="190" rx="14" fill="none" stroke="#01e69d" stroke-width="1.5" opacity=".6"/>
  <text class="lbl h" x="626" y="168" fill="#01e69d">Dedicated Logging Project</text>
  <text class="lbl s" x="626" y="186">High-throughput ingestion pipeline</text>

  <rect x="944" y="46" width="310" height="370" rx="14" fill="none" stroke="#FF216B" stroke-width="1.5" opacity=".7"/>
  <text class="lbl h" x="964" y="74" fill="#FF216B">Abstract Security SIEM</text>
  <text class="lbl s" x="964" y="92">Real-time correlation &amp; threat detection</text>

  <!-- Wires -->
  <use href="#p_waf" class="wire"/><use href="#p_ids" class="wire"/>
  <use href="#p_dns" class="wire"/><use href="#p_fw" class="wire"/>
  <use href="#p_pipe" class="wire"/><use href="#p_sub" class="wire"/>

  <!-- Sources -->
  <g class="lbl">
    <rect class="box" x="60" y="76" width="172" height="48" stroke="#2E9BF0"/>
    <text x="76" y="97" fill="#2E9BF0" font-size="13" font-weight="600">Cloud Armor WAF</text>
    <text x="76" y="114" class="s">OWASP CRS · DDoS blocks</text>

    <rect class="box" x="60" y="161" width="172" height="48" stroke="#FF216B"/>
    <text x="76" y="182" fill="#FF216B" font-size="13" font-weight="600">Cloud IDS</text>
    <text x="76" y="199" class="s">Snort exploits · malware C2</text>

    <rect class="box" x="60" y="246" width="172" height="48" stroke="#F5C61E"/>
    <text x="76" y="267" fill="#F5C61E" font-size="13" font-weight="600">VPC DNS Queries</text>
    <text x="76" y="284" class="s">DGA lookups · tunneling</text>

    <rect class="box" x="60" y="331" width="172" height="48" stroke="#01e69d"/>
    <text x="76" y="352" fill="#01e69d" font-size="13" font-weight="600">VPC Firewall Rules</text>
    <text x="76" y="369" class="s">L3/L4 ingress denies</text>
  </g>

  <!-- Log Router -->
  <g class="lbl">
    <rect class="box" x="430" y="202" width="100" height="56" stroke="#2e9bf0"/>
    <text x="480" y="226" text-anchor="middle" fill="#e9ecf1" font-size="13" font-weight="600">Log Router</text>
    <text x="480" y="243" text-anchor="middle" class="s">threat sink</text>
  </g>

  <!-- Topic + Sub -->
  <g class="lbl">
    <rect class="box" x="710" y="202" width="128" height="56" stroke="#01e69d"/>
    <text x="774" y="226" text-anchor="middle" fill="#e9ecf1" font-size="13" font-weight="600">Pub/Sub topic</text>
    <text x="774" y="243" text-anchor="middle" class="s">network-threats</text>

    <rect class="box" x="1010" y="202" width="166" height="56" stroke="#FF216B"/>
    <text x="1093" y="226" text-anchor="middle" fill="#e9ecf1" font-size="13" font-weight="600">Pull subscription</text>
    <text x="1093" y="243" text-anchor="middle" class="s">expiration: never</text>

    <rect class="box" x="1010" y="295" width="166" height="88" stroke="#FF216B"/>
    <text x="1093" y="337" text-anchor="middle" fill="#FFFFFF" font-size="28">⚡</text>
    <text x="1093" y="361" text-anchor="middle" fill="#FF216B" font-size="12.5" font-weight="700">Abstract SIEM</text>
    <text x="1093" y="375" text-anchor="middle" class="s">ECS network schema</text>
  </g>

  <!-- Permissions Callout -->
  <text class="lbl k" x="774" y="284" text-anchor="middle">writer identity needs</text>
  <text class="lbl k" x="774" y="299" text-anchor="middle">roles/pubsub.publisher</text>

  <!-- Animated Multi-Color Packets -->
  <g class="pk" filter="url(#glow)">
    <circle r="5" fill="url(#blue)"><animateMotion dur="2.8s" repeatCount="indefinite" begin="0s"><mpath href="#p_waf"/></animateMotion></circle>
    <circle r="5" fill="url(#pink)"><animateMotion dur="2.4s" repeatCount="indefinite" begin="0.5s"><mpath href="#p_ids"/></animateMotion></circle>
    <circle r="5" fill="url(#amber)"><animateMotion dur="2.6s" repeatCount="indefinite" begin="1.2s"><mpath href="#p_dns"/></animateMotion></circle>
    <circle r="5" fill="url(#teal)"><animateMotion dur="3.0s" repeatCount="indefinite" begin="1.8s"><mpath href="#p_fw"/></animateMotion></circle>

    <!-- Pipeline trunk packet trains -->
    <circle r="5.5" fill="url(#pink)"><animateMotion dur="1.5s" repeatCount="indefinite" begin="0.7s"><mpath href="#p_pipe"/></animateMotion></circle>
    <circle r="5.5" fill="url(#blue)"><animateMotion dur="1.5s" repeatCount="indefinite" begin="1.4s"><mpath href="#p_pipe"/></animateMotion></circle>

    <!-- Ingestion to Abstract -->
    <circle r="6" fill="url(#pink)"><animateMotion dur="1.6s" repeatCount="indefinite" begin="0.9s"><mpath href="#p_sub"/></animateMotion></circle>
    <circle r="6" fill="url(#teal)"><animateMotion dur="1.6s" repeatCount="indefinite" begin="1.7s"><mpath href="#p_sub"/></animateMotion></circle>
  </g>

  <!-- Detailed Legend & Flow Keymap at Bottom -->
  <g class="lbl" transform="translate(24, 440)">
    <rect x="0" y="0" width="1230" height="96" rx="10" fill="#0b0d13" stroke="#1f2330" stroke-width="1.2"/>

    <g transform="translate(24, 20)">
      <circle cx="10" cy="10" r="10" fill="#2E9BF0"/>
      <text x="10" y="14" text-anchor="middle" fill="#FFFFFF" font-size="11" font-weight="700">1</text>
      <text class="key-title" x="30" y="10" fill="#2E9BF0">Cloud Armor WAF</text>
      <text class="key-desc" x="30" y="26">L7 OWASP CRS &amp; rate limiting</text>
      <text class="key-desc" x="30" y="40">ALLOW / DENY decisions</text>
    </g>

    <g transform="translate(260, 20)">
      <circle cx="10" cy="10" r="10" fill="#FF216B"/>
      <text x="10" y="14" text-anchor="middle" fill="#FFFFFF" font-size="11" font-weight="700">2</text>
      <text class="key-title" x="30" y="10" fill="#FF216B">Cloud IDS Alerts</text>
      <text class="key-desc" x="30" y="26">Snort L4-L7 packet inspection</text>
      <text class="key-desc" x="30" y="40">C2, malware, exploit indicators</text>
    </g>

    <g transform="translate(500, 20)">
      <circle cx="10" cy="10" r="10" fill="#F5C61E"/>
      <text x="10" y="14" text-anchor="middle" fill="#FFFFFF" font-size="11" font-weight="700">3</text>
      <text class="key-title" x="30" y="10" fill="#F5C61E">VPC DNS Telemetry</text>
      <text class="key-desc" x="30" y="26">Query logging policy enabled</text>
      <text class="key-desc" x="30" y="40">Detects DGA &amp; exfil tunneling</text>
    </g>

    <g transform="translate(740, 20)">
      <circle cx="10" cy="10" r="10" fill="#01e69d"/>
      <text x="10" y="14" text-anchor="middle" fill="#FFFFFF" font-size="11" font-weight="700">4</text>
      <text class="key-title" x="30" y="10" fill="#01e69d">Firewall Flow Logs</text>
      <text class="key-desc" x="30" y="26">Ingress deny rule evaluations</text>
      <text class="key-desc" x="30" y="40">Internal reconnaissance tracking</text>
    </g>

    <g transform="translate(980, 20)">
      <circle cx="10" cy="10" r="10" fill="#FF216B"/>
      <text x="10" y="14" text-anchor="middle" fill="#FFFFFF" font-size="11" font-weight="700">5</text>
      <text class="key-title" x="30" y="10" fill="#FF216B">ACS Normalization</text>
      <text class="key-desc" x="30" y="26">source.ip, destination.ip</text>
      <text class="key-desc" x="30" y="40">threat.indicator, rule.name</text>
    </g>
  </g>
</svg>"""

    (diagrams_dir / "network-threats-animated.svg").write_text(nt_anim_svg, encoding="utf-8")

    # =========================================================================
    # 3. CREATE IDENTITY-AUTH-ANIMATED.SVG
    # =========================================================================
    id_anim_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1360 620" width="1360" height="620" role="img"
     aria-label="GCP and Workspace Identity Authentication Auditing Telemetry Flow into Abstract Security SIEM and OneUptime Canary Monitoring.">
  <title>GCP &amp; Workspace Identity Authentication Auditing Architecture</title>
  <defs>
    <linearGradient id="pink" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#FF216B"/><stop offset="100%" stop-color="#C2004C"/></linearGradient>
    <linearGradient id="teal" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#01e69d"/><stop offset="100%" stop-color="#008445"/></linearGradient>
    <linearGradient id="amber" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#F5C61E"/><stop offset="100%" stop-color="#D97706"/></linearGradient>
    <linearGradient id="blue" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#2E9BF0"/><stop offset="100%" stop-color="#1D4ED8"/></linearGradient>
    <radialGradient id="glow-ambient-left" cx="20%" cy="30%" r="50%">
      <stop offset="0%" stop-color="#2E9BF0" stop-opacity="0.12"/><stop offset="100%" stop-color="#060608" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glow-ambient-right" cx="85%" cy="35%" r="50%">
      <stop offset="0%" stop-color="#FF216B" stop-opacity="0.15"/><stop offset="100%" stop-color="#060608" stop-opacity="0"/>
    </radialGradient>
    <filter id="glow" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="4.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <pattern id="cyber-grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#161822" stroke-width="0.8" opacity="0.65"/>
    </pattern>

    <!-- Packet Motion Paths -->
    <path id="p_login" d="M210,95 H430 Q470,95 470,140 V200"/>
    <path id="p_sharing" d="M510,235 H710"/>
    <path id="p_impers" d="M210,180 H470"/>
    <path id="p_wif" d="M210,265 H470"/>
    <path id="p_keys" d="M210,350 H470"/>
    <path id="p_iam" d="M210,435 H430 Q470,435 470,390 V270"/>
    <path id="p_pipe" d="M550,235 H710"/>
    <path id="p_topic_sub" d="M780,265 V330"/>
    <path id="p_sub_abs" d="M838,360 H1010"/>
    <path id="p_sub_probe" d="M838,360 H920 Q950,360 950,470 H1010"/>

    <style>
      .lbl{font-family:Barlow,'Barlow Semi Condensed',-apple-system,sans-serif}
      .h{font-size:16px;font-weight:700;letter-spacing:.3px}
      .s{font-size:12px;fill:#8b8f98}
      .k{font-size:11px;fill:#f5c61e;font-family:'JetBrains Mono',monospace}
      .wire{stroke:#2a2d35;stroke-width:2.2;fill:none}
      .box{fill:#0d0f14;stroke:#1e2129;stroke-width:1.5;rx:10}
      .key-title{font-size:11px;font-weight:700;letter-spacing:0.5px;text-transform:uppercase}
      .key-desc{font-size:10.5px;fill:#8b8f98}
      @media (prefers-reduced-motion:reduce){.pk{display:none}}
    </style>
  </defs>

  <rect width="100%" height="100%" fill="#060608"/>
  <rect width="100%" height="100%" fill="url(#cyber-grid)"/>
  <rect width="100%" height="100%" fill="url(#glow-ambient-left)"/>
  <rect width="100%" height="100%" fill="url(#glow-ambient-right)"/>

  <!-- Live Pulse Status Badge -->
  <g class="lbl" transform="translate(1080, 20)">
    <rect x="0" y="0" width="240" height="26" rx="13" fill="#0d0f14" stroke="#01e69d" stroke-width="1.2"/>
    <circle cx="16" cy="13" r="4.5" fill="#01e69d" filter="url(#glow)">
      <animate attributeName="opacity" values="1;0.3;1" dur="1.5s" repeatCount="indefinite"/>
    </circle>
    <text x="28" y="17" fill="#01e69d" font-size="10.5" font-family="'JetBrains Mono',monospace" font-weight="600">ZERO SILENT FAILURE ACTIVE</text>
  </g>

  <!-- Containers -->
  <rect x="24" y="46" width="376" height="440" rx="14" fill="none" stroke="#2e9bf0" stroke-width="1.5" opacity=".6"/>
  <text class="lbl h" x="44" y="74" fill="#2e9bf0">5 Identity &amp; Auth Streams</text>
  <text class="lbl s" x="44" y="92">User logins · Impersonation · WIF · Keys · IAM</text>

  <rect x="424" y="140" width="470" height="260" rx="14" fill="none" stroke="#01e69d" stroke-width="1.5" opacity=".6"/>
  <text class="lbl h" x="444" y="168" fill="#01e69d">Aggregation &amp; Ingestion Pipeline</text>
  <text class="lbl s" x="444" y="186">Zero polling native audit sharing + Pub/Sub transport</text>

  <rect x="918" y="46" width="418" height="240" rx="14" fill="none" stroke="#FF216B" stroke-width="1.5" opacity=".7"/>
  <text class="lbl h" x="938" y="74" fill="#FF216B">Abstract Security SIEM</text>
  <text class="lbl s" x="938" y="92">6 Correlation Rules · ECS gcp.identity_auth</text>

  <rect x="918" y="306" width="418" height="180" rx="14" fill="none" stroke="#F5C61E" stroke-width="1.5" opacity=".7"/>
  <text class="lbl h" x="938" y="334" fill="#F5C61E">OneUptime Zero-Silent-Failure Canary</text>
  <text class="lbl s" x="938" y="352">Synthetic subscription probes · backpressure alerts</text>

  <!-- Wires -->
  <use href="#p_login" class="wire"/><use href="#p_impers" class="wire"/>
  <use href="#p_wif" class="wire"/><use href="#p_keys" class="wire"/><use href="#p_iam" class="wire"/>
  <use href="#p_pipe" class="wire"/><use href="#p_topic_sub" class="wire"/>
  <use href="#p_sub_abs" class="wire"/><use href="#p_sub_probe" class="wire"/>

  <!-- Identity Source Nodes -->
  <g class="lbl">
    <rect class="box" x="40" y="70" width="170" height="44" stroke="#2E9BF0"/>
    <text x="56" y="89" fill="#2E9BF0" font-size="12" font-weight="600">User Logins (Workspace)</text>
    <text x="56" y="104" class="s">login.googleapis.com (2SV)</text>

    <rect class="box" x="40" y="155" width="170" height="44" stroke="#FF216B"/>
    <text x="56" y="174" fill="#FF216B" font-size="12" font-weight="600">SA Impersonation</text>
    <text x="56" y="189" class="s">GenerateAccessToken (Data Access)</text>

    <rect class="box" x="40" y="240" width="170" height="44" stroke="#01e69d"/>
    <text x="56" y="259" fill="#01e69d" font-size="12" font-weight="600">Workload Identity (WIF)</text>
    <text x="56" y="274" class="s">GitHub Actions / AWS OIDC</text>

    <rect class="box" x="40" y="325" width="170" height="44" stroke="#F5C61E"/>
    <text x="56" y="344" fill="#F5C61E" font-size="12" font-weight="600">Static SA Key Auth</text>
    <text x="56" y="359" class="s">serviceAccountKeyName usage</text>

    <rect class="box" x="40" y="410" width="170" height="44" stroke="#2E9BF0"/>
    <text x="56" y="429" fill="#2E9BF0" font-size="12" font-weight="600">IAM Policy &amp; Denials</text>
    <text x="56" y="444" class="s">SetIamPolicy, CreateRole</text>
  </g>

  <!-- Pipeline Nodes -->
  <g class="lbl">
    <rect class="box" x="444" y="205" width="106" height="56" stroke="#2E9BF0"/>
    <text x="497" y="228" text-anchor="middle" fill="#e9ecf1" font-size="12" font-weight="600">Log Router</text>
    <text x="497" y="244" text-anchor="middle" class="s">aggregated sink</text>

    <rect class="box" x="710" y="205" width="128" height="56" stroke="#01e69d"/>
    <text x="774" y="228" text-anchor="middle" fill="#e9ecf1" font-size="12" font-weight="600">Pub/Sub topic</text>
    <text x="774" y="244" text-anchor="middle" class="s">abstract-audit-logs</text>

    <rect class="box" x="710" y="330" width="128" height="56" stroke="#FF216B"/>
    <text x="774" y="353" text-anchor="middle" fill="#e9ecf1" font-size="12" font-weight="600">Pull subscription</text>
    <text x="774" y="369" text-anchor="middle" class="s">never expires</text>
  </g>

  <!-- Abstract SIEM Nodes -->
  <g class="lbl">
    <rect class="box" x="940" y="120" width="160" height="66" stroke="#FF216B"/>
    <text x="1020" y="145" text-anchor="middle" fill="#FF216B" font-size="12.5" font-weight="700">SIEM Engine</text>
    <text x="1020" y="162" text-anchor="middle" class="s">ECS Normalization</text>

    <rect class="box" x="1130" y="120" width="180" height="66" stroke="#FF216B"/>
    <text x="1220" y="145" text-anchor="middle" fill="#e9ecf1" font-size="12" font-weight="600">6 SIEM Rules</text>
    <text x="1220" y="162" text-anchor="middle" class="s">Brute Force · Key Abuse · Geo</text>
  </g>

  <!-- OneUptime Nodes -->
  <g class="lbl">
    <rect class="box" x="940" y="380" width="160" height="66" stroke="#F5C61E"/>
    <text x="1020" y="405" text-anchor="middle" fill="#F5C61E" font-size="12.5" font-weight="700">Canary Probe</text>
    <text x="1020" y="422" text-anchor="middle" class="s">backlog lag testing</text>

    <rect class="box" x="1130" y="380" width="180" height="66" stroke="#F5C61E"/>
    <text x="1220" y="405" text-anchor="middle" fill="#e9ecf1" font-size="12" font-weight="600">Instant Alerting</text>
    <text x="1220" y="422" text-anchor="middle" class="s">PagerDuty / Slack on stall</text>
  </g>

  <!-- Animated Packets -->
  <g class="pk" filter="url(#glow)">
    <circle r="4.5" fill="url(#blue)"><animateMotion dur="3.0s" repeatCount="indefinite" begin="0s"><mpath href="#p_login"/></animateMotion></circle>
    <circle r="4.5" fill="url(#pink)"><animateMotion dur="2.6s" repeatCount="indefinite" begin="0.4s"><mpath href="#p_impers"/></animateMotion></circle>
    <circle r="4.5" fill="url(#teal)"><animateMotion dur="2.8s" repeatCount="indefinite" begin="0.8s"><mpath href="#p_wif"/></animateMotion></circle>
    <circle r="4.5" fill="url(#amber)"><animateMotion dur="3.2s" repeatCount="indefinite" begin="1.2s"><mpath href="#p_keys"/></animateMotion></circle>
    <circle r="4.5" fill="url(#blue)"><animateMotion dur="3.0s" repeatCount="indefinite" begin="1.6s"><mpath href="#p_iam"/></animateMotion></circle>

    <!-- Pipeline trunk & transport -->
    <circle r="5" fill="url(#pink)"><animateMotion dur="1.5s" repeatCount="indefinite" begin="0.7s"><mpath href="#p_pipe"/></animateMotion></circle>
    <circle r="5" fill="url(#teal)"><animateMotion dur="1.2s" repeatCount="indefinite" begin="0.9s"><mpath href="#p_topic_sub"/></animateMotion></circle>
    <circle r="5.5" fill="url(#pink)"><animateMotion dur="1.4s" repeatCount="indefinite" begin="1.1s"><mpath href="#p_sub_abs"/></animateMotion></circle>
    <circle r="5" fill="url(#amber)"><animateMotion dur="1.6s" repeatCount="indefinite" begin="1.3s"><mpath href="#p_sub_probe"/></animateMotion></circle>
  </g>

  <!-- Detailed Legend & Flow Keymap at Bottom -->
  <g class="lbl" transform="translate(24, 500)">
    <rect x="0" y="0" width="1312" height="96" rx="10" fill="#0b0d13" stroke="#1f2330" stroke-width="1.2"/>

    <g transform="translate(24, 20)">
      <circle cx="10" cy="10" r="10" fill="#2E9BF0"/>
      <text x="10" y="14" text-anchor="middle" fill="#FFFFFF" font-size="11" font-weight="700">1</text>
      <text class="key-title" x="30" y="10" fill="#2E9BF0">Native Workspace Audit</text>
      <text class="key-desc" x="30" y="26">Zero polling streaming export</text>
      <text class="key-desc" x="30" y="40">login.googleapis.com</text>
    </g>

    <g transform="translate(280, 20)">
      <circle cx="10" cy="10" r="10" fill="#FF216B"/>
      <text x="10" y="14" text-anchor="middle" fill="#FFFFFF" font-size="11" font-weight="700">2</text>
      <text class="key-title" x="30" y="10" fill="#FF216B">SA Impersonation Audit</text>
      <text class="key-desc" x="30" y="26">Requires DATA_ACCESS enabled</text>
      <text class="key-desc" x="30" y="40">iamcredentials GenerateAccessToken</text>
    </g>

    <g transform="translate(540, 20)">
      <circle cx="10" cy="10" r="10" fill="#01e69d"/>
      <text x="10" y="14" text-anchor="middle" fill="#FFFFFF" font-size="11" font-weight="700">3</text>
      <text class="key-title" x="30" y="10" fill="#01e69d">Workload Identity (WIF)</text>
      <text class="key-desc" x="30" y="26">Federated token exchange logs</text>
      <text class="key-desc" x="30" y="40">sts.googleapis.com (GitHub Actions)</text>
    </g>

    <g transform="translate(800, 20)">
      <circle cx="10" cy="10" r="10" fill="#FF216B"/>
      <text x="10" y="14" text-anchor="middle" fill="#FFFFFF" font-size="11" font-weight="700">4</text>
      <text class="key-title" x="30" y="10" fill="#FF216B">SIEM Detection Rules</text>
      <text class="key-desc" x="30" y="26">Brute force &amp; key anomaly detection</text>
      <text class="key-desc" x="30" y="40">ECS gcp.identity_auth schema</text>
    </g>

    <g transform="translate(1060, 20)">
      <circle cx="10" cy="10" r="10" fill="#F5C61E"/>
      <text x="10" y="14" text-anchor="middle" fill="#FFFFFF" font-size="11" font-weight="700">5</text>
      <text class="key-title" x="30" y="10" fill="#F5C61E">OneUptime Canary Probes</text>
      <text class="key-desc" x="30" y="26">Synthetic heartbeats detect silent stalls</text>
      <text class="key-desc" x="30" y="40">Backlog lag &gt; 300s alert</text>
    </g>
  </g>
</svg>"""

    (diagrams_dir / "identity-auth-animated.svg").write_text(id_anim_svg, encoding="utf-8")

    # =========================================================================
    # 4. RE-GENERATE STATICS VIA generate_diagram_assets.py
    # =========================================================================
    import generate_diagram_assets
    generate_diagram_assets.main()

    print("All animated and high-res diagram assets successfully built!")

if __name__ == "__main__":
    main()
