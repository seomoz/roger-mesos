ngx.req.read_body()
local data = ngx.req.get_body_data()
local res = ngx.location.capture("/auth-proxy", {body=data})

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

