import pandas as pd
import requests


season_id = "2024"

url = "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/2024/players?scoringPeriodId=0&view=players_wl"

league_id = "726244831"

espn_cookies = {"swid" : "{9B378FA4-FF7E-4A2E-9642-5BD40FA9792F}", "espn_s2" : "AECnQvlROrsEi9zJjkWEELp2Bf0pPwrHh/eSuOtiLzr33NBA50nx71JbZpUAoeH3RDxVyKri5IiEVkl7PicQApwvmVzKGeBrJBBh7CCwFOkCpEKdhVYDAKNvWICcmAiNikwma9KXhkxlBvpJe2npIlDVdHHt0zu4Ccnjv4rhroCVndy0bUOsXdNOQGfoXVF4HkMqLtd6kmHptSNAZHO/lTj/G14qarL+0ydl1VW67w5JI494t2aNhwARE0Zjrcko23YiEJmi6R4+lOTarHdONWePAPEEFJ58IO2xv9GTGfLrNy8uCN94K1iQjrWtGn01D/c="}

headers = {
    'Connection' : 'keep-alive',
    'Accept' : 'application/json, test/plain, */*',
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0',
    'x-fantasy-filter' : '{"filterActive":null}',
    'x-fantasy-platform' : 'kona-PROD-924d3c065ac5086e75ca68478d4e78341e18ba53',
    'x-fantasy-source' : 'kona'
}

r = requests.get(url, headers=headers, cookies = espn_cookies)

player_data = r.json()




df = pd.DataFrame(player_data)
print(df.sample(5))









