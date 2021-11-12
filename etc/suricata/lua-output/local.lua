function init (args)
    --print("Init LUA")
    json = require'lunajson'
    bs64 = require 'bs64'

    dir = "~/Documents/IDS/py/"

    print("Inicialização")
    os.execute(dir.."1_init.py")             --STATE: Inicialização

    local needs = {}
    needs["type"] = "packet"
    needs["filter"] = "alerts"
    return needs
end

function setup (args)
    
    verbose = false
    num_packets = 9

    tmst_table = {}
end

function log (args)
    sid, rev, gid = SCRuleIds()
    p = SCPacketPayload()
    
    if sid == 2 then
        --print("Match SID 2")
        -- print(p)
        local jsonparse = json.decode(p)
        local latitude = jsonparse["rxpk"][1]["latitude"]
        local longitude = jsonparse["rxpk"][1]["longitude"]
        local time = jsonparse["rxpk"][1]["time"]
        local datr = jsonparse["rxpk"][1]["datr"]
        local lsnr = jsonparse["rxpk"][1]["lsnr"]
        local rssi = jsonparse["rxpk"][1]["rssi"]
        local data = jsonparse["rxpk"][1]["data"]
        local payload = conv_payload(data)          --HEX payload
        local devaddr = reverseAddr(payload)        --REVERSE devaddr
        
        local sf = sf(datr)
        local bw = bw(datr)
        local tmst_actual = conv_time(time)*1000    --*1000 -> miliseconds
        local lenpayload = #payload                 --GET LEN of payload

        if tmst_table[devaddr] == None then         --IF device dont exist
            tmst_table[devaddr] = {tmst_actual,1}
            tmst_last = 0
            tmst_dif = tmst_last
            count = 1
        else                                        --IF exist
            tmst_last = tmst_table[devaddr][1]

            count = tmst_table[devaddr][2]
            count = count + 1
            tmst_table[devaddr] = {tmst_actual,count}--UPDATE new tmst and count
            tmst_dif = tmst_actual - tmst_last
        end

        local arg = " "..devaddr.." "..tmst_actual.." "..latitude.." "..longitude.." "..sf.." "..bw.." "..lsnr.." "..rssi.." "..lenpayload.." "..data.." "..tmst_last.." "..tmst_dif.." "..count
        
        if count < num_packets then                                      --STATE: Recolha de dados
            print("STATE -> Recolha de dados")
            os.execute(dir.."sqlclient.py"..arg)
        elseif count == num_packets then
            print("STATE -> 1 Aprendizagem")
            os.execute(dir.."2_auto_intrusions.py"..arg)                 --STATE: 1 Aprendizagem
            os.execute(dir.."3_train_model.py"..arg)
        else
            print("STATE -> Normal")
            os.execute(dir.."sqlclient.py"..arg)                         --STATE: Normal
            --nClock = os.clock()
            os.execute(dir.."machine.py"..arg)
            --print(os.clock()-nClock)
        end
        --print(tmst_last)
        --print(tmst_actual)
        --print(tmst_dif)
        --print(count)
        --print("____________")

        --os.execute("/home/phil/Documents/IDS/py/machine.py"..arg)
        --0,06 sec
        
    end
end

function deinit (args)

end

function conv_payload(data)
    if string.sub(data,-1,-1) == '=' then  --if base64
        data = tohex(base64_dec(data))
    end
    return data
end

function reverseAddr(s)
    return string.sub(s,9,10)..string.sub(s,7,8)..string.sub(s,5,6)..string.sub(s,3,4)
end

function sf(s)
    return string.sub(s,string.find(s,'F')+1, string.find(s,'B')-1)
end

function bw(s)
    return string.sub(s,string.find(s,'W')+1, -1)
end

function conv_time(json_date)
    -- from https://gist.github.com/zwh8800/9b0442efadc97408ffff248bc8573064#file-datetime-lua

    local pattern = "(%d+)%-(%d+)%-(%d+)%a(%d+)%:(%d+)%:([%d%.]+)([Z%+%-])(%d?%d?)%:?(%d?%d?)"
    local year, month, day, hour, minute, 
        seconds, offsetsign, offsethour, offsetmin = json_date:match(pattern)
    local timestamp = os.time{year = year, month = month, 
        day = day, hour = hour, min = minute, sec = seconds} - os.time{year=1970, month=1, day=1, hour=0}
    local offset = 0
    if offsetsign ~= 'Z' then
      offset = tonumber(offsethour) * 60 + tonumber(offsetmin)
      if xoffset == "-" then offset = offset * -1 end
    end
    
    return timestamp + offset * 60
end

function base64_dec(data)
    -- Lua 5.1+ base64 v3.0 (c) 2009 by Alex Kloss <alexthkloss@web.de>
    -- licensed under the terms of the LGPL2

    -- character table string
    local b='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
    data = string.gsub(data, '[^'..b..'=]', '')
    return (data:gsub('.', function(x)
        if (x == '=') then return '' end
        local r,f='',(b:find(x)-1)
        for i=6,1,-1 do r=r..(f%2^i-f%2^(i-1)>0 and '1' or '0') end
        return r;
    end):gsub('%d%d%d?%d?%d?%d?%d?%d?', function(x)
        if (#x ~= 8) then return '' end
        local c=0
        for i=1,8 do c=c+(x:sub(i,i)=='1' and 2^(8-i) or 0) end
        return string.char(c)
    end))
end

function tohex(str)
    return (str:gsub('.', function (c)
        return string.format('%02X', string.byte(c))
    end))
end

function print_list()
    for i,v in ipairs(l) do
        io.write(v)
    end
    print()
end
