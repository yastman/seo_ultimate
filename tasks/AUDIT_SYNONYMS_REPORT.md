============================================================
АУДИТ РАЗДЕЛЕНИЯ KEYWORDS/SYNONYMS
============================================================
Traceback (most recent call last):
  File "C:\Users\user\Documents\Сайты\Ultimate.net.ua\сео_для_категорий_ультимейт\scripts\audit_synonyms.py", line 144, in <module>
    main()
  File "C:\Users\user\Documents\Сайты\Ultimate.net.ua\сео_для_категорий_ультимейт\scripts\audit_synonyms.py", line 109, in main
    print(f"\n\U0001f4c1 Проверено категорий: {len(all_issues) + len(json_errors)}")
  File "C:\Users\user\AppData\Local\Programs\Python\Python312\Lib\encodings\cp1251.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f4c1' in position 2: character maps to <undefined>
