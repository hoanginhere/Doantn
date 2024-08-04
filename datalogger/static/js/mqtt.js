// Tạo một kết nối MQTT
var client = new Paho.MQTT.Client("broker.emqx.io", Number(1883), "clientId");

// Đăng ký hàm xử lý khi kết nối thành công
client.onConnectionLost = onConnectionLost;
client.onMessageArrived = onMessageArrived;

// Kết nối tới broker MQTT
client.connect({ onSuccess: onConnect });

// Hàm xử lý khi kết nối thành công
function onConnect() {
    console.log("Connected to MQTT broker");
    client.subscribe("sensor/1"); // Thay thế bằng chủ đề MQTT bạn muốn subscribe
}

// Hàm xử lý khi mất kết nối
function onConnectionLost(responseObject) {
    if (responseObject.errorCode !== 0) {
        console.log("Connection lost: " + responseObject.errorMessage);
    }
}

// Hàm xử lý khi nhận được tin nhắn MQTT
function onMessageArrived(message) {
    var payload = message.payloadString;
    console.log("Received message: " + payload);

    // Gửi dữ liệu nhận được đến máy chủ Django thông qua AJAX
    $.ajax({
        url: "/mqtt-data/", // Đường dẫn tới view Django xử lý dữ liệu MQTT
        type: "POST",
        data: { payload: payload },
        success: function(response) {
            console.log("Data sent to Django server");
        },
        error: function(xhr, status, error) {
            console.log("Error sending data to Django server: " + error);
        }
    });
}