#!/usr/bin/env python

def check_balanced(s):

  par_state=""

  string_mode=False
  string_type=None
  escaped=False

  line_comment_mode=False
  half_line_comment_marker=False

  multiline_comment_mode=False
  half_multiline_comment_marker=False

  for c in s:

    if string_mode:

      if escaped:
        escaped = False

      elif c == "\\":
        escaped = True

      elif c == string_type:
        string_mode = False

    elif line_comment_mode:

      if c == "\n":
        line_comment_mode = False

    elif multiline_comment_mode:

      if c == "*":
        half_multiline_comment_marker = True

      else:
        if c == "/" and half_multiline_comment_marker:
          multiline_comment_mode = False
        half_multiline_comment_marker = False

    else:

      if c in "\"\'":
        string_mode = True
        string_type = c

      elif c == "/":
        if half_line_comment_marker:
          half_line_comment_marker = False
          half_multiline_comment_marker = False
          line_comment_mode = True
        else:
          half_line_comment_marker = True
          half_multiline_comment_marker = True

      elif c == "*":
        if half_multiline_comment_marker:
          half_line_comment_marker = False
          half_multiline_comment_marker = False
          multiline_comment_mode = True

      elif c in "{[(":
        par_state += c

      elif c=="}":
        if len(par_state)==0 or par_state[-1]!="{":
          return "invalid"
        par_state = par_state[:-1]

      elif c==")":
        if len(par_state)==0 or par_state[-1]!="(":
          return "invalid"
        par_state = par_state[:-1]

      elif c=="]":
        if len(par_state)==0 or par_state[-1]!="[":
          return "invalid"
        par_state = par_state[:-1]

      else:
        half_line_comment_marker = False
        half_multiline_comment_marker = False

  if string_mode or multiline_comment_mode or len(par_state)>0:
    return "incomplete"
  else:
    return "complete"

def check(s):
  status = check_balanced(s)
  if status == "incomplete":
    return (status, s, "error: unbalanced expression")
  elif status == "invalid":
    return (status, s, "error: unbalanced expression")
  s = s.rstrip()
  if len(s) == 0 or s[-1] != ";":
    return ("incomplete", s, "error: missing semicolon")
  return ("complete", s, None)
