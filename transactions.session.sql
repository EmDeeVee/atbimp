SELECT * from [transaction] t
WHERE account_id = 6 and date = "20220-04-01"
ORDER BY t.date, t.id desc
;