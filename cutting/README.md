# Audio clipping and smoothing service
## Описание
Микросервис для вырезания из аудио фрагментов и сглаживания образующихся склеек

На вход ожидает 2 файла:
1. mp3
2. json с timestamp


Json выглядит следующим образом:
<pre>
{"redundants":
  [
    {
      "start": *время начала*, 
      "end": *время конца*, 
      "filler": {
        -- либо "empty", либо "bleep"
        "empty" : {
          -- либо "cross_fade", либо "fade_in_out"
          "cross_fade" : число/null/{}
          "fade_in_out": {
            "fade_in": число/null,
            "fade_out": число/null
           } 
           -- в случае если не указан какой-то из fade_ будет взято значение по умолчанию
        }
        "bleep": {} (пустой словарь или null)
      }
    },
  ]
}
</pre>

В случае если указан некорректный cross_fade, например если cross_fade указан 3000, а одна из склеиваемых сторон меньше, будет использоваться максимально возможный cross_fade. 


Запуск тестов:
------------
    python3 tests/utils/test_cut_file.py
------------

Запуск в докере:
------------
    docker pull polonium13/cutting:version
    docker run --log-driver=json-file -d -p 8002:8002 -it polonium13/cutting:version
------------
