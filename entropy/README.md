# Оценка энтропии источников случайности

Для статистического оценивания энтропии источников случайности рекомендуется 
использовать средство `EntropyAssessment`, разработанное в Национальном 
институте стандартов и технологий (NIST) США. Исходные тексты программ 
`EntropyAssessment`, а также сопутствующие материалы размещены по адресу
[https://github.com/usnistgov/SP800-90B_EntropyAssessment](https://github.com/usnistgov/SP800-90B_EntropyAssessment).

Сборка `EntropyAssessment` в соответствии с 
[документацией](https://github.com/usnistgov/SP800-90B_EntropyAssessment/blob/master/README.md) 
средства реализована в скрипте `build.sh`. Скрипт следует скопировать в 
подходящий рабочий каталог и выполнить. 

При успешном выполнении `build.sh` в рабочем каталоге будет создан вложенный 
каталог `.build`. Он будет содержать исполняемые файлы `ea_XXX`, 
предназначенными для оценки энтропии, а также каталог `SP800-90B_EntropyAssessment` 
с исходными текстами средства `EntropyAssessment`. 

Работа с программами `ea_XXX` описана в 
[документации](https://github.com/usnistgov/SP800-90B_EntropyAssessment/blob/master/README.md).

