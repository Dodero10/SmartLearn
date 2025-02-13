const API_URL = "http://localhost:8030";

/**
 * Service xử lý các tương tác chat với backend
 */
export const chatService = {
  /**
   * Gửi tin nhắn đến server và nhận phản hồi một lần
   *
   * @param {string} message - Nội dung tin nhắn cần gửi
   * @param {string} sessionId - ID phiên chat
   * @param {function} onChunk - Callback xử lý khi nhận được phản hồi
   * @returns {Promise<string>} Phản hồi từ server
   */
  sendMessage: async (message, sessionId, onChunk = (chunk) => {}) => {
    try {
      const response = await fetch(`${API_URL}/api/v1/chat/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: message,
          thread_id: sessionId,
        }),
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await response.json();
      onChunk(data.answer);
      return data.answer;
    } catch (error) {
      console.error("Chat service error:", error);
      throw error;
    }
  },

  /**
   * Gửi tin nhắn đến server và nhận phản hồi dạng stream
   *
   * @param {string} message - Nội dung tin nhắn cần gửi
   * @param {string} sessionId - ID phiên chat
   * @param {string} model - ID model được chọn
   * @param {function} onToken - Callback xử lý từng token nhận được
   * @param {function} onError - Callback xử lý khi có lỗi
   */
  sendMessageStream: async (
    message, // Nội dung tin nhắn từ người dùng
    sessionId, // ID của phiên chat hiện tại
    model, // ID model được chọn
    onToken = (token) => {}, // Callback được gọi mỗi khi nhận được token mới
    onError = (error) => {} // Callback xử lý lỗi
  ) => {
    try {
      // Gửi request POST đến API endpoint
      const response = await fetch(`${API_URL}/api/v1/chat/chat/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        // Đóng gói dữ liệu gửi đi
        body: JSON.stringify({
          question: message,
          thread_id: sessionId,
          model: model,
        }),
      });

      // Kiểm tra response status, ném lỗi nếu không thành công
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      // Khởi tạo reader để đọc dữ liệu stream
      const reader = response.body.getReader();
      // Tạo decoder để chuyển đổi dữ liệu nhị phân thành text
      const decoder = new TextDecoder();

      // Vòng lặp vô hạn để đọc stream cho đến khi kết thúc
      while (true) {
        // Đọc một chunk dữ liệu từ stream
        const { value, done } = await reader.read();
        // Nếu đã đọc xong thì thoát vòng lặp
        if (done) break;

        // Chuyển đổi chunk dữ liệu thành text
        const chunk = decoder.decode(value);
        // Tách chunk thành các dòng và lọc
        // - Loại bỏ dòng trống
        // - Chỉ lấy dòng bắt đầu bằng "data: "
        const lines = chunk
          .split("\n")
          .filter((line) => line.trim() !== "" && line.startsWith("data: "));

        // Xử lý từng dòng SSE (Server-Sent Events)
        for (const line of lines) {
          try {
            // Bỏ prefix "data: " và parse JSON
            const jsonStr = line.replace("data: ", "");
            const json = JSON.parse(jsonStr);

            // Kiểm tra nếu server trả về lỗi
            if (json.error) {
              onError(json.error); // Gọi callback xử lý lỗi
              return; // Kết thúc xử lý
            }

            // Nếu có nội dung, gửi token đến UI qua callback
            if (json.content) {
              onToken(json.content);
            }
          } catch (e) {
            // Xử lý lỗi khi parse JSON thất bại
            console.error("Error parsing SSE message:", e);
          }
        }
      }
    } catch (error) {
      // Xử lý các lỗi khác (network, stream, etc.)
      console.error("Stream error:", error);
      onError(error.message); // Thông báo lỗi cho UI
    }
  },
};
