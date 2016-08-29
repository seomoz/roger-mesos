ngx.req.read_body()
local data = ngx.req.get_body_data()
ngx.req.set_header("auth_action", "auth")
local res = ngx.location.capture("/auth", {body=data})

if res.status == ngx.HTTP_OK then
    ngx.exit(ngx.OK)
end

if res.status == ngx.HTTP_FORBIDDEN then
    ngx.exit(res.status)
end

if res.status == ngx.HTTP_UNAUTHORIZED then
    ngx.exit(res.status)
end

ngx.exit(ngx.HTTP_INTERNAL_SERVER_ERROR)
