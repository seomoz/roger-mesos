ngx.req.read_body()
local req_data = ngx.req.get_body_data()
ngx.req.set_header("auth_action", "auth")
local req_res = ngx.location.capture("/auth-proxy", {body=req_data})

if req_res.status == ngx.HTTP_FORBIDDEN then
    ngx.exit(req_res.status)
end

if req_res.status == ngx.HTTP_UNAUTHORIZED then
    ngx.exit(req_res.status)
end

if req_res.status ~= ngx.HTTP_OK then
    ngx.exit(ngx.HTTP_INTERNAL_SERVER_ERROR)
end

local res = ngx.location.capture(ngx.var.location_endpoint, { copy_all_vars = true })

if res.status == ngx.HTTP_FORBIDDEN then
    ngx.exit(res.status)
end

if res.status == ngx.HTTP_UNAUTHORIZED then
    ngx.exit(res.status)
end

if res.status ~= ngx.HTTP_OK then
    ngx.exit(ngx.HTTP_INTERNAL_SERVER_ERROR)
end

local data = res.body

ngx.req.set_header("auth_action", "filter_response")
local resp = ngx.location.capture("/auth-proxy", {body=data})

if resp.status == ngx.HTTP_OK then
    ngx.header["Content-Type"] = "application/json; qs=2"  
    ngx.header["Pragma"] = "no-cache"
    ngx.header["Expires"] = 0
    ngx.header["Connection"] = "close"
    ngx.send_headers()
    -- The print() should be only after all headers are sent
    ngx.print(resp.body)
    ngx.exit(ngx.OK)
end

if resp.status == ngx.HTTP_FORBIDDEN then
    ngx.exit(resp.status)
end

if resp.status == ngx.HTTP_UNAUTHORIZED then
    ngx.exit(resp.status)
end

ngx.exit(resp.status)


