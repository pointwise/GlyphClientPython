#! /usr/bin/env python

#############################################################################
#
# (C) 2021 Cadence Design Systems, Inc. All rights reserved worldwide.
#
# This sample script is not supported by Cadence Design Systems, Inc.
# It is provided freely for demonstration purposes only.
# SEE THE WARRANTY DISCLAIMER AT THE BOTTOM OF THIS FILE.
#
#############################################################################

"""
This module provides a Python-like interface to Glyph.

GlyphObj provides the service of automatically converting Python
function calls into the equivalent Glyph command string and creates
Python objects to represent Glyph classes and objects.

GlyphVar provides a convenient interface for representing Tcl variables
as Python objects for Glyph commands that accept Tcl variable names as
arguments. These are typically used to return some optional Glyph result
value.
"""

from pointwise import GlyphClient, GlyphError
import keyword, json, re

class GlyphVar(object):
    """ A GlyphVar object wraps a Tcl variable name that may be passed to
        a Glyph action, which is typically used to return some value
        that is not the return value from the action. A variable name
        can be supplied; if not, a temporary Tcl variable name will be
        generated.

        Tcl:
            pw::Display selectEntities -selectionmask $mask ents

        where 'ents' is a Tcl variable name

        Python:
            m = pw.Display.createSelectionMask(requireConnector="Dimensioned")
            entsVar = GlyphVar()
            pw.Display.selectEntities(entsVar, selectionMask=m)
            cons = entsVar["Connectors"]

        where 'entsVar' is a GlyphVar object containing the 'ents' result value
    """

    def __init__(self, varname=None, value=None):
        """ Initializes GlyphVar object with its initial value """
        self.value = value
        self.varname_ = varname

    def __getitem__(self, item):
        """ Allows the GlyphVar to be subscriptable if applicable """
        return self.value[item]

    def __setitem__(self, key, value):
        """ Allows the GlyphVar to have values assigned to it if applicable """
        self.value[key] = value

    def __iter__(self):
        """ Allows the GlyphVar to be iterable """
        return (e for e in self.value)


class GlyphObj(object):
    """ This class implements a wrapper around Glyph Objects. In this context,
        a Glyph object can be a Glyph function (instance) for instance actions,
        or a Glyph class for static actions.
    """

    # pre-compiled regular expression matching Glyph function (object) names
    _functionRE = re.compile(r"::pw::[a-zA-Z]+_\d+( |$)")

    def __init__(self, function, glf):
        """ Glyph object constructor from a Glyph function name. Glyph wrappers
            are typically created automatically from the result of other Glyph
            actions.

            Args:
                function - the glyph function name or JSON dict with
                    command element

                glf - the GlyphClient connection in use

            Example:
                con = GlyphObj("pw::Connector_1", pw)
        """
        self.glf = glf
        if isinstance(function, dict):
            self._function = function['command']
            self._type = function['type']
        else:
            self._function = function
            if GlyphObj._functionRE.match(function):
                self._type = glf.eval("%s getType" % function)
            else:
                self._type = None

    def __enter__(self):
        """ Glyph objects derived from pw::Mode or pw::Examine can be
            used as context managers. For modes, the context will
            automatically issue the 'mode end' action upon exit, unless
            an exception occurs in which case 'mode abort' will be issued.
            Examine, the Glyph examine object will be destroyed when the
            context exits.

            Ex.
                with pw.Application.begin("Create") as creator:
                    con = pw.Connector()
                    ...

                with pw.Examine("BlockJacobian") as exam:
                    exam.addEntity(blk)
                    exam.examine()
                    ...
        """
        self._isMode = self._isExamine = self._open = False

        try:
            x = self.glf.eval(self._function + " isOfType pw::Examine")
            self._isExamine = bool(int(x))
        except Exception:
            self._isExamine = False

        if not self._isExamine:
            try:
                x = self.glf.eval(self._function + " isOfType pw::Mode")
                self._isMode = bool(int(x))
            except Exception:
                self._isMode = False

        if self._isMode:
            self._open = True

            def _end():
                try:
                    self.glf.eval(self._function + " end")
                    self._open = False
                except:
                    pass

            setattr(self, "end", _end)
        elif self._isExamine:
            self._open = True

            def _delete():
                try:
                    self.glf.eval(self._function + " delete")
                    self._open = False
                except:
                    pass

            setattr(self, "delete", _delete)
        else:
            raise GlyphError("", "A GlyphObj can be used as a context " + \
                    "manager for mode and examine objects only.")

        return self


    def __exit__(self, ex_type, ex_val, ex_tb):
        """ Exit context, ending or aborting mode or deleting examine object
            as needed
        """
        try:
            if self._open:
                if self._isMode:
                    if ex_type is None:
                        self.glf.eval(self._function + " end")
                    else:
                        self.glf.eval(self._function + " abort")
                elif self._isExamine:
                    self.glf.eval(self._function + " delete")
                self._open = False
                return False
        finally:
            del self._isMode
            del self._isExamine
            del self._open


    # Create Glyph object when called
    def __call__(self, *args):
        """ Creates GlyphObj from the result of the glyph command
                '<glyph-class> create'. This is valid only for
                objects that represent Glyph classes that implement
                the 'create' action.

            Args:
                args - a list of positional arguments to be passed to
                    the Glyph 'create' action

            Returns:
                GlyphObj object that was created

            Example:
                con = pw.Connector()
                exa = pw.Examine("ConnectorLengthI")
        """
        gvars = {}
        kwargs = {}
        cmd = self._buildGlyphCmd(self._function, 'create', args, kwargs, gvars)
        result = self._runGlyphCmd(cmd)
        return result


    def __str__(self):
        """ Returns a string representation of the Glyph object. """
        name = self.glf.eval("if [%s isOfType pw::Entity] { %s getName }" % \
                (self._function, self._function))
        return "%s (%s)" % (self._function, name)


    # Method for comparing GlyphObj objects            
    def __eq__(self, other):
        """ Compare two Glyph objects for equality. Glyph objects are
            equal if their Glyph functions refer to the same Glyph object.

            Returns:
                True if GlyphObj objects refer to the same Glyph object.
        """
        cmd = [self._function, 'equals', other._function]
        return bool(self._runGlyphCmd(cmd))


    # Add hash support so GlyphObj objects can be used in dictionaries
    def __hash__(self):
        return hash(self._function)


    @property
    def glyphType(self):
        """ Return the Glyph type of a GlyphObj. """
        return self._type


    @staticmethod
    def _toGlyph(value, varDict):
        """ Helper function to process a Glyph result value. """
        result = None
        if isinstance(value, GlyphVar):
            # Create variable in Glyph and store its reference name in varDict
            if value.varname_ is None:
                value.varname_ = '_TMPvar_%d' % len(varDict)
            result = value.varname_
            varDict[value] = result
        elif isinstance(value, GlyphObj):
            # Substitute the Glyph function name
            result = value._function
        elif isinstance(value, str):
            # Handle string arguments
            result = value
        else:
            try:
                # See if the object is iterable
                it = iter(value)
                result = [GlyphObj._toGlyph(v, varDict) for v in it]
            except:
                result = value
                pass

        return result


    @staticmethod
    def _buildGlyphCmd(function, action, args, kwargs, gvars):
        """ Helper function that builds command list to be converted to JSON. 

            Args: 
                function: the Glyph object or class on which the action
                    is to be run

                action: the Glyph action to be run on the Glyph object or class

                args - list of non-keyword (positional) arguments for the
                    Glyph action. Positional arguments always appear at
                    the end of a Glyph action, after all command switches.

                kwargs - list of keyword (switch) arguments for the Glyph
                    action. Switch arguments always appear immediately
                    after the action name. The following rules apply
                    when keyward arguments are present:

                    - the keyword is added to the Glyph command as a switch
                        (e.g., '-orient')
                    - if the keyword argument value is None, the switch
                        has no arguments in the action
                    - if the keyword argument value is a scalar (non-list)
                        value, the value is added right after the switch
                        (e.g., '-orient Best')
                    - if the keyword argument value is a list, a Tcl
                        list is added right after the switch, UNLESS the
                        keyword itself has a trailing underscore. In that
                        case, the list arguments are added one at a time
                        after the switch. For example,

                        Python               Tcl
                        arg=[s1, s2]   => -arg [list s1 s2]
                        arg_=[s1, s2]  => -arg s1 s2

                gvars: dictionary used to keep track of Glyph variables. Key
                    is GlyphVar object and value is Glyph variable name

            Returns: 
                JSON serializable list to be sent to _runGlyphCmd function
        """
        cmd = []

        # Some glyph commands are python keywords, and so must be passed with
        # a trailing underscore
        if keyword.iskeyword(action[:-1]) and action[-1] == '_':
            action = action[:-1]

        cmd.append(function)
        cmd.append(action)

        # Add keyword args as flags first (Glyph standard command notation)
        for flag, value in kwargs.items():
            # special convention for flags that accept multiple arguments:
            #    foo  = [a, b]           => -foo {a b}
            #    foo_ = [a, b]           => -foo a b
            #    foo  = [[a, b], [c, d]] => -foo {{a b} {c d}}
            #    foo_ = [[a, b], [c, d]] => -foo {a b} {c d}

            # special convention for keywords with boolean values:
            #   foo=True    => -foo
            #   foo_=True   => -foo true
            #   foo=False   => (flag excluded from command)
            #   foo_=False  => -foo false
            
            flatten = flag.endswith('_')

            if flatten:
                flag = flag[:-1]

            if not flatten and isinstance(value, bool) and bool(value) == False:
                continue

            gval = GlyphObj._toGlyph(value, gvars)

            cmd.append("-%s" % flag)

            if flatten:
                cmd += gval
            elif not isinstance(value, bool):
                cmd.append(gval)

        # Add positional args (never flattened) to the command
        cmd += [GlyphObj._toGlyph(arg, gvars) for arg in args]

        return cmd


    @staticmethod
    def _isGlyphFunction(arg):
        """ Helper function to determine if an object or list of objects can
            be converted to a GlyphObj

            Args:
                arg - element to check if it is something returned from JSON

            Returns:
                True if element can be converted to a GlyphObj
        """

        if isinstance(arg, dict):
            # JSON result from Glyph action
            return all(k in arg for k in ('command', 'type'))
        elif isinstance(arg, str) and GlyphObj._functionRE.match(arg):
            # Glyph function name
            return True
        else:
            return False


    def _runGlyphCmd(self, cmd):
        """ Helper function to run a Glyph action that is represented as
            a list of string command arguments

            Args:
                cmd - A JSON serializable list that represents the Glyph action

            Returns:
                Return value from Glyph action, converted to a GlyphObj if
                    possible
        """

        # convert the command list to a JSON string, execute the command, and 
        # convert the result back from a JSON string to a Python list
        result = json.loads(self.glf.command(json.dumps(cmd)))

        # If the result is a list, convert any JSON dict elements to GlyphObj
        # Note: this doesn't allow for nested lists of Glyph objects
        if isinstance(result, list):
            result = [self._toPythonObj(k) for k in result]
        else:
            result = self._toPythonObj(result)

        return result


    def __getattr__(self, action):
        """ Create a method on demand that mimics some Glyph action.
            Note: Glyph action names that conflict with Python reserved words
            must be appended with an underscore. E.g.
            
            pw.Grid.import_(filename)
        """
        def _action_(*args, **kwargs):
            """ Used to generate Glyph calls 'on the fly'. A JSON command is
                created based on the GlyphObj action called. The value that
                is returned from the server is then converted back to GlyphObj
                object if applicable.

                Returns:
                    Whatever Glyph command would return as GlyphObj object
                    type if applicable
            """
            function = self._function  

            # dict of GlyphObj (Tcl variable)
            gvars = {}

            # create command token list
            cmd = self._buildGlyphCmd(function, action, args, kwargs, gvars)
            try:
                result = self._runGlyphCmd(cmd)
                # evaluate Glyph variable contents
                if gvars:
                    for pyVar, tclVarName in gvars.items():
                        pyVar.value = self._evalTclVar(tclVarName)
                    self._delTclVar(gvars)
                if self._isMode and action in ['end', 'abort']:
                    self._open = False
                elif self._isExamine and action == 'delete':
                    self._open = False
                return result
            except GlyphError:
                raise

        setattr(self, action, _action_)
        return _action_ 


    def _delTclVar(self, gvars):
        """ Helper function to delete (unset) a dictionary of Glyph (Tcl)
            variables

            Args:
                gvars - dictionary of Glyph variables with key as
                    GlyphVar object and value as Glyph name

            Returns:
                None
        """
        _unset = "if [info exists %s] { unset %s }"
        cmd = [(_unset % (var, var)) for var in gvars.values()]
        self.glf.eval('; '.join(cmd))


    def _toPythonObj(self, tclArg):
        """ Helper function to convert a Tcl string to a Python string or
            GlyphObj object

            Args:
                tclArg - item to convert

            Returns:
                Python string or GlyphObj
        """
        result = tclArg
        if GlyphObj._isGlyphFunction(tclArg):
            result = GlyphObj(tclArg, self.glf)
        elif isinstance(tclArg, str):
            tclArg = tclArg.strip()
            if len(tclArg) > 0:
                try:
                    result = int(tclArg)
                except ValueError:
                    try:
                        result = float(tclArg)
                    except ValueError:
                        result = tclArg
            else:
                result = None
        return result


    def _toPythonList(self, tclArg):
        """ Helper function to convert a Tcl list to a Python list, converting
            Glyph function names to GlyphObj objects where possible. The
            input list can be as deeply nested as needed, and the resulting
            Python list will be nested to the same depth. Tcl strings that can
            be converted to numeric Python objects will be so converted.

            Args:
                tclArg - Tcl list or value to be converted to Python list of
                    string or GlyphObj values. A Tcl list must be in the
                    form "{ v1 v2 v3 }". Nested Tcl lists are handled.

                Tcl                            Python
                { { 0 0 1 } { 0 1 0 } }     => [[0, 0, 1], [0, 1, 0]]

                { 0.0 1.0 ::pw::Surface_1 } => [0.0, 1.0, gobj]
                    where gobj = GlyphObj("::pw::Surface_1")

                {::pw::Surface_1 ::pw::Connector_1 } => [gobj1, gobj2]
                    where gobj1 = GlyphObj("::pw::Surface_1")
                          gobj2 = GlyphObj("::pw::Connector_1")

            Returns:
                Python list where every element is a string, number, or
                GlyphObj object
        """
        out = []
        cache = [out]
        element = ''
        escape = False
        for char in tclArg:
            if escape:
                if char not in ["\\", "{", "}", "[", "]", "$"]:
                    raise ValueError("Incorrect escape character %s" % char)
                element += char
                escape = False
            elif char == "\\":
                escape = True
            elif char in [" ", "\t", "\r", "\n"]:
                element = self._toPythonObj(element)
                if element is not None:
                    cache[-1].append(element)
                element = ''
            elif char == "{":
                level = []
                cache[-1].append(level)
                cache.append(level)
            elif char == "}":
                if len(cache) < 2:
                    raise ValueError("Close bracket without opening bracket.")
                element = self._toPythonObj(element)
                if element is not None:
                    cache[-1].append(element)
                cache.pop()
                element = ''
            else:
                element += char

        element = self._toPythonObj(element)
        if element is not None:
            cache[-1].append(element)

        if len(cache) != 1:
            raise ValueError("Mismatched brackets.")

        if len(out) == 1:
            out = out[0]
        return out


    def _evalTclVar(self, tclVarName):
        """ Evaluate a Tcl variable and convert to Python. A Tcl array will
            be converted to a Python dictionary. All other Tcl values will
            be converted to a list of Python values.
            
            Note: scalar Tcl values will be returned as a list with a
            single element. Values that are Glyph functions (objects)
            will be converted to GlyphObj objects.

            Args:
                tclVarName - Glyph variable name to be evaluated and
                    stored in a Python dictionary or list

            Returns: 
                A Python Dictionary
        """
        # ask Tcl interpreter if the variable exists
        isvar = int(self.glf.eval("info exists %s" % tclVarName))
        if not isvar:
            return None

        # ask Tcl interpreter if the variable is an array
        isdict = int(self.glf.eval("array exists %s" % tclVarName))
        if isdict:
            # Convert Tcl array to Python dict
            tcl = self.glf.eval("array get %s" % tclVarName)
        else:
            # Convert Tcl list (or single value) to a Python list
            tcl = self.glf.eval("lrange $%s 0 end" % tclVarName)

        result = self._toPythonList(tcl)

        if isdict:
            # make each dictionary value a list as needed
            i = iter(result)
            result = dict(zip(i, i))
            for key, value in result.items():
                if not isinstance(value, list):
                    result[key] = [value]

        return result

#############################################################################
#
# This file is licensed under the Cadence Public License Version 1.0 (the
# "License"), a copy of which is found in the included file named "LICENSE",
# and is distributed "AS IS." TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE
# LAW, CADENCE DISCLAIMS ALL WARRANTIES AND IN NO EVENT SHALL BE LIABLE TO
# ANY PARTY FOR ANY DAMAGES ARISING OUT OF OR RELATING TO USE OF THIS FILE.
# Please see the License for the full text of applicable terms.
#
#############################################################################
