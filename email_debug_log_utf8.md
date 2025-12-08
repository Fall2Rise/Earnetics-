--- SMTP DEBUGGER ---
Server: smtp.gmail.com
Port: 587
Email: selfbuilddigital@gmail.com
Password: *******************
Connecting to smtp.gmail.com:587...
python : Traceback (most recent call last):
At line:1 char:1
+ python scripts/debug_email.py > 
email_debug_log.txt 2>&1
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~
    + CategoryInfo          : NotSpecified: (Trac 
   eback (most recent call last)::String) [], Re  
  moteException
    + FullyQualifiedErrorId : NativeCommandError
 
  File "C:\AI_Projects\Fallat_CrewAI\scripts\debug
_email.py", line 30, in debug_smtp
    print("\u2705 Connected.")
  File "C:\Users\Joshua\AppData\Local\Programs\Pyt
hon\Python312\Lib\encodings\cp1252.py", line 19, 
in encode
    return codecs.charmap_encode(input,self.errors
,encoding_table)[0]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'charmap' codec can't encode 
character '\u2705' in position 0: character maps 
to <undefined>

During handling of the above exception, another 
exception occurred:

Traceback (most recent call last):
  File "C:\AI_Projects\Fallat_CrewAI\scripts\debug
_email.py", line 50, in <module>
    debug_smtp()
  File "C:\AI_Projects\Fallat_CrewAI\scripts\debug
_email.py", line 47, in debug_smtp
    print(f"\u274c CONNECTION ERROR: {e}")
  File "C:\Users\Joshua\AppData\Local\Programs\Pyt
hon\Python312\Lib\encodings\cp1252.py", line 19, 
in encode
    return codecs.charmap_encode(input,self.errors
,encoding_table)[0]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'charmap' codec can't encode 
character '\u274c' in position 0: character maps 
to <undefined>
