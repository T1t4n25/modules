# Localization Module

Used if we have multiple languages to return messages in.

#### Sectons:

1. How to Use
2. How it works

---

## How to use

1. for every request, set language using ``locale_context`` module with ``set_locale()`` function, default is ``en``
   - you can also set middleware to apply it to all requests
   - setting up a global dependancy won't work as global dependancies don't share context with the request
2. import ``Localizer`` Class from localizer
3. make an object & give it the main logger you use, Note that it's a singleton class, so you can use it anywhere in your code without giving it parameters
4. Messages are to be saved in the locales folder, json file name is the language name, keys are shared between languages but messages are different from one language to another
5. when you want to get a message use ``get_message()``, pass the key used in the json files, language is taken automatically with ``locale_context``

---

## How it works

1. a context variable is set having the language to use for every request that is recieved, and it's used in the ``Localizer`` object
2. ``Localizer`` object initializes itself by setting a logger, and loading locales to memory from json files in ``locales`` folder, using the files names as the language name, and using lang name as a key in the dictionary to access another dictionary having a key indicating the message, and the value is the message itself written in the language specified

```
{
    "ar": {
        "msg1": "ok"
    },
    "en": {
        "msg1": "تمام"
    }
}
```

3. ``get_message()`` function takes 1 main argument that is the ``key`` to access full message, and ``kwargs`` for any customized strings that needs to be put in the message string
   *example*: ``"An unexpected error occurred. Error ID: {error_id}. Please provide this ID to the developer."``
   in this case we can call ``get_messages(key, error_id="123")``, and the code formats it to the messages string.
4. Calls are cached to reduce redundant calls, and has  hard limit of 512 cached messages, edit if needed, the limit acts as a protection against developer errors only, and it doens't cache calls with extra parameters like error_id as it's variable to reduce cache size to only constant messages
