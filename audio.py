import pyttsx3
# import tamil

def audio(name):
    # content = open("audio.txt", 'r')
    # file1 = open("audio.txt", "r+")
    # out = 'raja'
    out = f'hello {name}'
    print(out)
    engine = pyttsx3.init()

    # engine.setProperty('voice', "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\MSTTS_V110_taIN_ValluvarM")
    # engine.setProperty('voice')
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate-75)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    # languages = engine.getProperty('-languages')
    # for language in languages:
    #     print(language)
    # for voice in voices:
    #     print(" - Languages: %s" % voice.languages)
    #     engine.setProperty('voice', voices[1].id)
    #     # engine.setProperty('language', language = 'ta')
    engine.say(out)
    engine.runAndWait()

    # voices = engine.getProperty('voices')
    # rate = engine.getProperty('rate')
    # print(rate)
    # engine.setProperty('rate', rate-75)
    # for voice in voices:
    # engine.setProperty('voice', voice.id[1])
    # print(voice.id)
    # engine.say(out)
    # engine.runAndWait()