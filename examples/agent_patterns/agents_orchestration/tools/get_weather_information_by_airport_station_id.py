import asyncio
import requests
import json
import os
from agents import (
    Agent,
    ModelSettings,
    Runner,
    function_tool,
    trace,
)
from call_mcp_tool import call_mcp_tool

@function_tool(
    name_override="get_weather_information",
    description_override="Fetch official detailed weather, flight risk assessment and natural language METAR explanation",
)
def get_weather_information(airportStationId: str) -> str:
    response = call_mcp_tool(
        "get_weather_information_by_airport_station_id",
        {"airportStationId": airportStationId},
    )

    weather_json_str = response["result"]["content"][0]["text"]
    data = json.loads(weather_json_str)

    # =========================
    # Parse mây
    # =========================
    cloud_meaning = {
        "FEW": "Ít mây (1–2/8 bầu trời)",
        "SCT": "Mây rải rác (3–4/8 bầu trời)",
        "BKN": "Mây nhiều (5–7/8 bầu trời)",
        "OVC": "Trời phủ kín (8/8 bầu trời)",
    }

    clouds_detail = "Không có mây đáng kể"
    if data.get("clouds"):
        try:
            clouds = json.loads(data["clouds"])
            clouds_detail = "\n".join(
                [
                    f"- {c['cover']}: {cloud_meaning.get(c['cover'], 'Không xác định')} ở độ cao {c['base']} ft"
                    for c in clouds
                ]
            )
        except Exception:
            clouds_detail = data["clouds"]

    # =========================
    # Đánh giá gió (gió chéo / gió mạnh)
    # =========================
    wind_warning = ""
    wspd = int(data.get("wspd", 0))
    if wspd >= 20:
        wind_warning = "⚠️ Gió mạnh, có thể ảnh hưởng cất/hạ cánh"
    elif wspd >= 12:
        wind_warning = "⚠️ Gió trung bình, cần theo dõi gió chéo"
    else:
        wind_warning = "✅ Gió nhẹ, ít ảnh hưởng khai thác"

    # =========================
    # Đánh giá rủi ro delay/hủy
    # =========================
    flt_cat = data.get("fltCat")
    risk_map = {
        "VFR": "🟢 Rủi ro thấp – điều kiện bay tốt, ít khả năng delay",
        "MVFR": "🟡 Rủi ro trung bình – có thể hạn chế khai thác",
        "IFR": "🟠 Rủi ro cao – dễ xảy ra delay",
        "LIFR": "🔴 Rủi ro rất cao – nguy cơ delay hoặc hủy chuyến",
    }
    flight_risk = risk_map.get(flt_cat, "Không xác định")

    # =========================
    # Diễn giải METAR tự nhiên
    # =========================
    metar_explain = (
        f"Tại sân bay {data['icaoId']}, thời tiết hiện tại có nhiệt độ {data['temp']}°C, "
        f"điểm sương {data['dewp']}°C. Gió thổi từ hướng {data['wdir']}° "
        f"với tốc độ {data['wspd']} knot. Tầm nhìn ngang đạt {data['visib']}. "
        f"Áp suất khí quyển ở mức {data['altim']} hPa. "
        f"Điều kiện mây: {clouds_detail.splitlines()[0] if clouds_detail else 'không đáng kể'}."
    )

    return (
        "✈️ BÁO CÁO THỜI TIẾT & ĐÁNH GIÁ KHAI THÁC BAY (CHÍNH THỨC)\n"
        "====================================================\n"
        f"🏷️ Sân bay: {data['name']} ({data['icaoId']})\n"
        f"🕒 Thời gian báo cáo: {data['reportTime']}\n\n"

        "🌡️ ĐIỀU KIỆN KHÍ TƯỢNG\n"
        f"- Nhiệt độ: {data['temp']}°C\n"
        f"- Điểm sương: {data['dewp']}°C\n"
        f"- Áp suất (QNH): {data['altim']} hPa\n"
        f"- Tầm nhìn: {data['visib']}\n\n"

        "💨 GIÓ & CẢNH BÁO\n"
        f"- Hướng gió: {data['wdir']}°\n"
        f"- Tốc độ gió: {data['wspd']} kt\n"
        f"- Đánh giá: {wind_warning}\n\n"

        "☁️ MÂY\n"
        f"{clouds_detail}\n\n"

        "✈️ PHÂN LOẠI BAY (FLT CATEGORY)\n"
        "VFR  : Bay bằng mắt – điều kiện tốt\n"
        "MVFR : Bay hạn chế\n"
        "IFR  : Bay bằng thiết bị\n"
        "LIFR : Rất xấu – dễ delay/hủy\n\n"
        f"👉 Phân loại hiện tại: {flt_cat}\n\n"

        "⏱️ ĐÁNH GIÁ RỦI RO DELAY / HỦY CHUYẾN\n"
        f"{flight_risk}\n\n"

        "🗣️ DIỄN GIẢI METAR (NGÔN NGỮ TỰ NHIÊN)\n"
        f"{metar_explain}\n\n"

        "📡 METAR GỐC\n"
        f"{data['rawOb']}"
    )