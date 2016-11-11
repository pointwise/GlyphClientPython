# GlyphClientPython

Python implementation of a client which communicates with the Pointwise Glyph Server.

Example usage::

    from pointwise import GlyphClient, GlyphError

    glf = GlyphClient()
    if glf.connect():
        try:
            result = glf.eval('pw::Application getVersion')
            print('Pointwise version is {0}'.format(result))
        except GlyphError as e:
            print('Error in command {0}\n{1}'.format(e.command, e))

    elif glf.is_busy():
        print('The Glyph Server is busy')
    elif glf.auth_failed():
        print('Glyph Server authentication failed')
    else:
        print('Failed to connect to the Glyph Server')
