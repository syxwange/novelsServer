
#include "common.h"

#include <crow.h>
int main()
{
    
    crow::SimpleApp app;
    app.loglevel(crow::LogLevel::WARNING);
    CROW_ROUTE(app, "/")([]() {return "Hello world!";});

    CROW_ROUTE(app, "/image")([](){
        std::ifstream file("image2.jpg", std::ios::binary);
        if (file) {
            file.seekg(0, std::ios::end);
            std::streamsize size = file.tellg();
            file.seekg(0, std::ios::beg);

            std::vector<char> buffer(size);
            if (file.read(buffer.data(), size)) {
                crow::response res;
                res.set_header("Content-Type", "image/jpeg");
                res.write(std::string(buffer.data(), size));
                return res;
            }
        }
        return crow::response(404);
    });

    //使用静态文件
    CROW_ROUTE(app, "/img/<str>")([](const crow::request&, crow::response& res,const std::string& img){
        res.set_static_file_info(img);
        res.end();
    });

    CROW_CATCHALL_ROUTE(app) ([](crow::response& res) {
        res.code =503;       
        res.body = "Service Unavailable.";       
        res.end();
    });
    
    // app.port(443).ssl_file("server.pem", "server.key").run();
    app.port(80).multithreaded().run();
    return 0;
}