import asyncio
from agents import Agent, ModelSettings, Runner, trace
from tools.get_airport_locations import get_airport_locations
from tools.get_flight_informations_by_particular_fields import get_flight_information
from tools.get_weather_information_by_airport_station_id import get_weather_information
from tools.resolve_airport_location import resolve_airport_location
from tools.calculate_route import calculate_route


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
# Location Agent (CHỈ xử lý resolve location)
# ==================================================
location_agent = Agent(
    name="Location Agent",
    model="gpt-4o-mini",
    instructions=(
        "Bạn là nhân viên định vị sân bay.\n"
        "MỌI câu hỏi liên quan đến tên sân bay, vị trí, tọa độ → BẮT BUỘC gọi tool.\n"
        "Không suy đoán, không tự gán tọa độ.\n"
        "Chỉ trả về dữ liệu từ tool.\n"
        "Sau khi có kết quả, trả về đầy đủ thông tin tọa độ (latitude, longitude) để agent khác sử dụng.\n"
        "QUAN TRỌNG: Bạn chỉ cung cấp tọa độ. Bạn KHÔNG trả lời câu hỏi về thời gian di chuyển hay quãng đường."
    ),
    model_settings=ModelSettings(tool_choice="required"),
    tools=[resolve_airport_location],
)

# ==================================================
# Routing Agent (CHỈ xử lý route – luôn gọi tool)
# ==================================================
routing_agent = Agent(
    name="Routing Agent",
    model="gpt-4o-mini",
    instructions=(
        "Bạn là nhân viên điều phối mặt đất.\n"
        "MỌI câu hỏi về thời gian di chuyển, quãng đường, ETA → BẮT BUỘC gọi tool routing.\n"
        "Bạn sẽ nhận được tọa độ từ Location Agent trong cuộc trò chuyện.\n"
        "Đọc kỹ tọa độ (latitude, longitude) từ cuộc trò chuyện trước đó.\n"
        "Sử dụng tọa độ đó để gọi tool calculate_route với các tham số: from_latitude, from_longitude, to_latitude, to_longitude.\n"
        "Sử dụng dữ liệu traffic nếu có.\n"
        "Không suy đoán ngoài dữ liệu tool."
    ),
    model_settings=ModelSettings(tool_choice="required"),
    tools=[calculate_route],
)

# ==================================================
# Airport Locations Agent (DANH SÁCH SÂN BAY)
# ==================================================
airport_locations_agent = Agent(
    name="Airport Locations Data Agent",
    model="gpt-4o-mini",
    instructions=(
        "Bạn là agent CUNG CẤP DỮ LIỆU sân bay.\n"
        "\n"
        "VAI TRÒ DUY NHẤT:\n"
        "- GỌI tool get_airport_locations để lấy TOÀN BỘ danh sách sân bay và tọa độ.\n"
        "\n"
        "QUY TẮC BẮT BUỘC:\n"
        "1. LUÔN gọi tool get_airport_locations.\n"
        "2. KHÔNG lọc, KHÔNG tìm sân bay cụ thể.\n"
        "3. KHÔNG suy luận, KHÔNG diễn giải.\n"
        "4. KHÔNG trả lời người dùng cuối.\n"
        "5. Trả kết quả NGUYÊN DỮ LIỆU từ tool để agent khác xử lý.\n"
        "\n"
        "DỮ LIỆU TRẢ VỀ sẽ được agent khác sử dụng để:\n"
        "- Tìm sân bay tương ứng\n"
        "- Trích xuất tọa độ chính xác\n"
        "- Tính toán routing"
    ),
    model_settings=ModelSettings(tool_choice="required"),
    tools=[get_airport_locations],
)


# ==================================================
# Orchestrator Agent (ĐIỀU PHỐI)
# ==================================================
# Give orchestrator direct access to ALL tools to maintain full control over the sequence
orchestrator = Agent(
    name="Aviation & Ground Orchestrator",
    model="gpt-4o-mini",
    instructions=(
        "Bạn là điều phối viên hàng không & mặt đất.\n"
        "NHIỆM VỤ: Xử lý TẤT CẢ các yêu cầu trong câu hỏi, KHÔNG được bỏ sót bất kỳ phần nào.\n"
        "\n"
        "QUY TRÌNH BẮT BUỘC (XỬ LÝ TẤT CẢ CÁC PHẦN):\n"
        "\n"
        "BƯỚC 1: Phân tích câu hỏi để xác định TẤT CẢ các yêu cầu:\n"
        "  - Yêu cầu về chuyến bay? (sử dụng get_flight_information)\n"
        "  - Yêu cầu về thời tiết? (sử dụng get_weather_information)\n"
        "  - Yêu cầu về di chuyển mặt đất? (sử dụng resolve_airport_location + calculate_route)\n"
        "  - Yêu cầu danh sách sân bay hoặc tọa độ hàng loạt? (sử dụng get_airport_locations)\n"
        "\n"
        "BƯỚC 2: Xử lý TẤT CẢ các yêu cầu đã xác định:\n"
        "\n"
        "  A) Nếu có yêu cầu chuyến bay:\n"
        "     → Gọi tool get_flight_information với các tham số phù hợp\n"
        "\n"
        "  B) Nếu có yêu cầu thời tiết (để đánh giá delay, nguy cơ, v.v.):\n"
        "     → Gọi tool get_weather_information với station_id của sân bay (ví dụ: 'VVTS' cho Tân Sơn Nhất)\n"
        "\n"
        "  C) Nếu có yêu cầu di chuyển mặt đất (tính thời gian, quãng đường, ETA):\n"
        "       KHI CẦN TỌA ĐỘ CHO MỘT ĐIỂM, BẮT BUỘC XÁC ĐỊNH LOẠI ĐIỂM:\n"
        "\n"
        "  C.1) ĐIỂM LÀ SÂN BAY\n"
        "  (ví dụ: Sân bay Tân Sơn Nhất, SGN, HAN, ICAO, airport)\n"
        "  → TUYỆT ĐỐI KHÔNG gọi resolve_airport_location\n"
        "  → BẮT BUỘC thực hiện ĐÚNG THỨ TỰ:\n"
        "     1) Gọi Airport Locations Data Agent (tool get_airport_locations)\n"
        "     2) Lấy latitude / longitude từ kết quả matching\n"
        "\n"
        "  C.2) ĐIỂM KHÔNG PHẢI SÂN BAY\n"
        "  (ví dụ: quận, khách sạn, địa chỉ, POI)\n"
        "  → BẮT BUỘC gọi tool resolve_airport_location để lấy tọa độ.\n"
        "  C.3) SAU KHI CÓ TỌA ĐỘ CẢ HAI ĐIỂM\n"
        "  → Gọi tool calculate_route với:\n"
        "     - from_latitude, from_longitude\n"
        "     - to_latitude, to_longitude\n"
        "     - travel_mode='car' (nếu là ô tô)\n"
        "     - traffic=True (nếu có xét giao thông)\n"
        "\n"
        "\n"
        "\n"
        "BƯỚC 3: Tổng hợp TẤT CẢ kết quả:\n"
        "  - Thông tin chuyến bay (nếu có)\n"
        "  - Thông tin thời tiết và đánh giá nguy cơ delay (nếu có)\n"
        "  - Thông tin thời gian/quãng đường di chuyển (nếu có)\n"
        "  - CHỈ SAU KHI có TẤT CẢ kết quả, bạn mới được tổng hợp và trả lời\n"
        "\n"
        "QUY TẮC CỰC KỲ QUAN TRỌNG:\n"
        "1. BẠN PHẢI xử lý TẤT CẢ các phần trong câu hỏi. KHÔNG được bỏ sót.\n"
        "2. Nếu câu hỏi có nhiều phần (ví dụ: chuyến bay + thời tiết + di chuyển), bạn PHẢI xử lý CẢ BA.\n"
        "3. Sau mỗi tool call, bạn PHẢI kiểm tra: 'Tôi đã xử lý TẤT CẢ các yêu cầu chưa?'\n"
        "4. Đối với di chuyển mặt đất: PHẢI gọi tool get_airport_locations để lấy tọa độ sân bay và gọi tool resolve_airport_location để lấy tọa độ điểm còn lại TRƯỚC KHI gọi calculate_route.\n"
        "5. KHÔNG được kết thúc nếu còn thiếu bất kỳ phần nào của câu hỏi.\n"
        "6. Đọc kỹ tọa độ từ kết quả resolve_airport_location với tọa độ từ kết quả get_airport_locations và truyền chính xác vào calculate_route.\n"
        "7. Bạn có thể gọi các tool theo bất kỳ thứ tự nào, nhưng PHẢI gọi TẤT CẢ các tool cần thiết.\n"
        "\n"
        "LUỒNG XỬ LÝ TỌA ĐỘ SÂN BAY (BẮT BUỘC):\n"

        "a) Gọi Airport Locations Data Agent để lấy TOÀN BỘ danh sách sân bay và tìm sân bay phù hợp nhất\n"
        "b) Đọc latitude / longitude từ kết quả matching\n"
        "c) Gọi calculate_route với tọa độ đã được match\n"

        "PHÂN BIỆT TRÁCH NHIỆM:\n"
        "- Airport Locations Data Agent → LẤY DỮ LIỆU VÀ TÌM SÂN BAY TƯƠNG ỨNG\n"
        "- calculate_route → TÍNH TOÁN\n"

        "VÍ DỤ: Câu hỏi có 3 phần:\n"
        "  - 'Cho tôi các chuyến bay từ A đến B' → gọi get_flight_information\n"
        "  - 'đánh giá nguy cơ delay dựa trên thời tiết' → gọi get_weather_information\n"
        "  - 'ước tính thời gian di chuyển từ X đến Y' → gọi resolve_airport_location (2 lần) + calculate_route\n"
        "→ BẠN PHẢI xử lý CẢ BA phần trước khi kết thúc."
    ),
    model_settings=ModelSettings(tool_choice="auto"),
    tools=[
        get_flight_information,
        get_weather_information,
        resolve_airport_location,
        calculate_route,
        get_airport_locations,
    ],  # All tools directly accessible
)

# Note: After location_agent and routing_agent complete their tasks,
# control automatically returns to the orchestrator with the full conversation history.
# The orchestrator will then continue based on its instructions.


# ==================================================
# MAIN
# ==================================================
# ==================================================
# MAIN
# ==================================================
async def main():
    with trace("Aviation & Ground – Complex Query"):
        question = (
            "Cho tôi các chuyến bay từ Hà Nội (HAN) đi Sài Gòn (SGN), "
            "đánh giá nguy cơ delay dựa trên thời tiết Sân Bay Tân Sơn Nhất, "
            "ước tính thời gian di chuyển từ Sân Bay Tân Sơn Nhất "
            "đến Quận 1 bằng ô tô, có xét giao thông."
        )

        result = await Runner.run(
            orchestrator,
            question,
        )

        print("\n===== FINAL ANSWER =====\n")
        print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
