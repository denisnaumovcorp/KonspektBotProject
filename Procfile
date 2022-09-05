heroku login адньфыеуктв"пьфшдюсщь 6Ф5с2978)
heroku create --region eu konspektbotproject
#P.S. в имени могут быть только буквы в нижнем регитсре, цифры  и тире.
heroku addons:create heroku-redis:hobby-dev -a konspektbotproject #И снова меняем имя!
heroku buildpacks:set heroku/python
git push heroku master
heroku ps:scale KonspektBot=1 # запускаем бота
heroku logs --tail #включаем логи
