#!/bin/bash

address_array=("1EKu91dzRTisAF4ZdBQ9gzwpmY6bDC3HHZnvCQ"
    "1FwSwQHg1UGJGA6RH56QSfoqj3qNRVAMGh3cNx"
    "1HcuPeTicjCWJszmMo1kHjFZGToFkGvnuEPwky"
    "13tuyQPofomieAZg9c9gXf3UWfKBE4RxC8VXat"
    "1T3hY9STWUkQsLQzrGgaXdMwLKLsfCqhq5uPqK"
    "1K1fCn6M59H6wNUY8JCP9A6AFRjSHehsUGxToZ"
    "1PDgiGztvKBCiyp5dU6begH9AjSyjHfiCWNdwX"
    "16bknt6CoT6Z8ahhTXBACHupULcBW54VJVTtmS"
    "1TDmE1PL4GRQxdp8eSYwwxpVM35V3KhgurWMkB"
    "1SyhKNEPnearnSKnc6sQZCJ6FwedJQViqVDePx"
    "1aFcikB9jJb7gHfghDhUzVgRoBVHCG3YYKaKgy"
    "1G7AQXLywxgQXPuKZS2hZupkaVfXCkMeCURkFM"
    "15xsNZjFc3femZejJk8PrqR9c4R8H6TFJGBLMC"
    "1CQtegWgAaFgyWTiQmZxxE4otEAjjT6wcRZnj"
    "1S3Lo3L1Wz3McHKgodCFxd6khAt6udzLz1W6dc"
    "1Rgg7hPnQZsf4oTVpNhaoa3tF8NWFB6qkb4PGk"
    "1RXKAWeaxdVjpDgXkoQ9PqGL2FRwvJDqF76rsY"
    "1DEs9ztsMmRRtQC1yGivEQfQHSXESUgKsAh2wV"
    "1TpBbhyCmVSmbZES4xZTcdW2hbatWezQGrYejR"
    "1S4AmnfouSujXLEjkHjRDF1n9VK9p3tNgxTYek"
    "1CApwYPKa7hYufJcQnTuDyPe2cJobVZH3ra22U"
    "15u4eYzrmYd9ygVjB5hVhd15veBPnXfEhm6upg"
    "1NCiUZAkp4GZ2y5fm6Xx1QpUw13Tag8nRkaa1N"
    "1UHHqgtorTdurZsYSSaK7cv2TnSuZDxPt13pcM"
    "1PWWecwL41tESRDuvLL8oR5RJMadHHzNAPX3Y2"
    "1AkoLR58NMQF2v2PRjkAqU5ZWsWWHKZR7B5XQ5"
    "16SMYYf8UVGDLG2DHfR4CuSLJ4Sg9CCcvpnkR9"
    "17qrh4uRV64XwfhLV8hyCHN6FAHGXqXWtoNzyc"
    "1GqrBgmRdMJDzXpF3x9LzUq5RVmxRpK1ZCgVAM"
    "1RES8ZqF56brjgr6U7Xgm9uWRVWuSy2T2jekrF"
    "1TqjEs6YyEoD1Jzs9J1qdwzz1wsE8ELQNz5j8g"
    "17ZbUNrq3ZsW8ntiNJm31TBVW6V4ee9DDreQSf"
    "18zQwF3wJo6LgdxhPhs2t4aEWyN9szjtBUTfuj"
    "1TSTrDZmNqyfDr1RkJVVHX9T6yu6iJME8zvHhw"
    "1Ln1tu5YgeV54t1wmyVPmLoWzTPfz2U9P6jkCt"
    "1EaQaxNY74s7XNsvapQDx3Swv7kmAszGHbBAJC"
    "1R1iYqGNoanXCuXFePJZuneHFx9xNLUNFPEXy4"
    "1Gn64LLeXVCzNtt4Me8bMNKuNP8q7Y2qukUCJU")

for i in "${address_array[@]}"
do
	multichain-cli auditchain sendassetfrom "1DiLpyvbwDNsG3LrPuuoWW8aSj3mc6svG7wCZx" "$i" "USD" 200000 
done