import asyncio
from agents import Agent, ModelSettings, Runner, trace
from tools.get_flight_informations_by_particular_fields import get_flight_information
from tools.get_weather_information_by_airport_station_id import get_weather_information


# ==================================================
# Flight Agent (CHỈ xử lý flight – luôn gọi tool)
# ==================================================
flight_agent = Agent(
    name="Flight Agent",
    model="gpt-4o-mini",
    instructions=(
        "Bạn là nhân viên khai thác bay.\n"
        "MỌI câu hỏi liên quan đến chuyến bay, lịch bay, trạng thái bay → BẮT BUỘC gọi tool.\n"
        "Không suy đoán, không dùng kiến thức ngoài dữ liệu tool.\n"
        "Trả lời bằng tiếng Việt, ngắn gọn, rõ ràng."
    ),
    model_settings=ModelSettings(tool_choice="required"),
    tools=[get_flight_information],
)


# ==================================================
# Weather Agent (CHỈ xử lý METAR – luôn gọi tool)
# ==================================================
weather_agent = Agent(
    name="Weather Agent",
    model="gpt-4o-mini",
    instructions=(
        "Bạn là nhân viên khí tượng hàng không.\n"
        "MỌI câu hỏi về thời tiết sân bay → BẮT BUỘC gọi tool METAR.\n"
        "Chuyển METAR sang tiếng Việt tự nhiên.\n"
        "Nêu rõ: gió, mây (FEW/SCT/BKN/OVC), tầm nhìn, fltCat.\n"
        "Không suy đoán ngoài dữ liệu tool."
    ),
    model_settings=ModelSettings(tool_choice="required"),
    tools=[get_weather_information],
)


# ==================================================
# Orchestrator Agent (ĐIỀU PHỐI)
# ==================================================
orchestrator = Agent(
    name="Aviation Orchestrator",
    model="gpt-4o-mini",
    instructions=(
        "Bạn là điều phối viên hàng không.\n"
        "Nhiệm vụ:\n"
        "1. Xác định người dùng cần THÔNG TIN BAY, THỜI TIẾT hay CẢ HAI.\n"
        "2. Gọi ĐÚNG agent chuyên trách.\n"
        "3. Tổng hợp kết quả, KHÔNG bịa, KHÔNG thêm dữ liệu ngoài.\n"
        "4. Nếu có đủ flight + weather → đánh giá nguy cơ delay/hủy dựa trên fltCat & gió.\n"
        "Chỉ dùng dữ liệu do agent con trả về."
    ),
    model_settings=ModelSettings(tool_choice="auto"),
    handoffs=[flight_agent, weather_agent],
)


# ==================================================
# MAIN
# ==================================================
async def main():
    with trace("Aviation Orchestrator – Complex Query"):
        question = (
            "Cho tôi các chuyến bay từ Hà Nội (HAN) đi Sài Gòn (SGN) "
            "và đánh giá nguy cơ delay dựa trên thời tiết sân bay Tân Sơn Nhất (VVTS)"
        )

        result = await Runner.run(
            orchestrator,
            question,
        )

        print("\n===== FINAL ANSWER =====\n")
        print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
