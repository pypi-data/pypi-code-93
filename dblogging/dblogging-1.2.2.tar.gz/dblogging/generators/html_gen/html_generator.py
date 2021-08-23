from typing import List, Dict, Optional, Tuple, Union
import os
import shutil
import re
import uuid
from pathlib import Path
from datetime import datetime
from pygments import highlight
from pygments.lexers.python import PythonLexer
from pygments.formatters.html import HtmlFormatter
import htmlmin
from dblogging.sqlite.dal import LoggerSql, SelectResult
from dblogging.config import LogTag

ACTION_JS = """
// Escape regex key characters
RegExp.escape = function(string) {
  return string.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&')
};

// Toggle (De)compression Class
function toggleCompression(el, compress=null) {
    if(compress !== null) {
        if(compress === true) {
            el.classList.replace('decompressed', 'compressed');
        } else {
            el.classList.replace('compressed', 'decompressed');
        }
    } else {
        el.classList.toggle('compressed');
        el.classList.toggle('decompressed');
    }
}

// Toggle Display None/Block
function toggleShowHide(el, hide=null) {
   if(hide !== null) {
       if(hide === true) {
           el.classList.replace('show', 'hide');
       } else {
           el.classList.replace('hide', 'show');
       }
   } else {
       el.classList.toggle('hide');
       el.classList.toggle('show');
   }
}

// Hide/Show Filters Container
function handleShowFilter(filters_btn) {
    filters = document.getElementById('filters');
    toggleCompression(filters);
    filters_btn.textContent = filters.classList.contains('decompressed') ? "Hide Filters" : "Show Filters";
}

/* Log Content Handles */
// Expand Subsequent Logs With Same Depth
function expandLogs(log_entry) {
    log_entry.classList.add('expanded');
    exp_btn = log_entry.querySelector('.exp-btn');
    exp_btn.classList.replace('hide-logs', 'show-logs');
    depth = log_entry.getAttribute('aria-label');
    // For each sibling...
    for(var i=log_entry.nextElementSibling; i!==null; i=i.nextElementSibling) {
        if(Number(i.getAttribute('aria-label')) == (Number(depth) + 1)) {
            // If the depth of this log entry is the same as the original entry, show it.
            toggleShowHide(i, hide=false);
        }
        else if (Number(i.getAttribute('aria-label')) > (Number(depth) + 1)) {
            // If the depth is greater, it is a child entry of another log. Just skip it.
            continue;
        }
        else {
            // The depth of this entry belongs to a parent depth. Stop looping.
            break;
        }
    }
}
// Collapse Subsequent Logs Of Greater Depth
function collapseLogs(log_entry) {
    log_entry.classList.remove('expanded');
    exp_btn = log_entry.querySelector('.exp-btn');
    if(exp_btn) {
        // If the entry has child entries, toggle the arrow of the exp btn.
        exp_btn.classList.replace('show-logs', 'hide-logs');
    }
    depth = log_entry.getAttribute('aria-label');
    // For each sibling...
    for(var i=log_entry.nextElementSibling; i!==null; i=i.nextElementSibling) {
        if(depth < i.getAttribute('aria-label')) {
            // If the depth of the original entry is less than this one, then this is a
            // descendant entry. Hide it.
            toggleShowHide(i, hide=true);
            exp_btn = i.querySelector('.exp-btn');
            if(exp_btn) {
                // If the exp btn exists, set the arrow to hide.
                exp_btn.classList.replace('show-logs', 'hide-logs');
            }
        }
        else {
            // This entry belongs to a parent depth. Stop looping.
            break;
        }
    }
}

// Toggle Log Expansion
function toggleExpLogs(log_entry_id) {
    log_entry = document.getElementById(log_entry_id);
    if(!log_entry_id) {
        return;
    }
    if(log_entry.classList.contains('expanded')) {
        collapseLogs(log_entry);
    }
    else {
        expandLogs(log_entry);
    }
}

// Show/Hide Log Message/Info Block And Highlight Button Text
function handleLogContent(btn, block_id, hide=null) {
    block = document.getElementById(block_id);
    toggleShowHide(block, hide);
    if(hide === true) {
        btn.classList.remove('bold');
    } else if(hide === false) {
        btn.classList.add('bold');
    } else {
        btn.classList.toggle('bold');
    }
}

// Handle Code Blocks
function showCode(file_id, file_name, line_num) {
    // Show the code blocks panel.
    code_blocks = document.querySelector('#code-blocks');
    code_blocks.classList.replace('hide', 'show');

    // Get the code block div and show it.
    code_block = document.querySelector('#'+file_id);
    code_block.classList.replace('hide', 'show');

    // Get the code block object tag and scroll it to the top of the panel.
    code = code_block.querySelector('.code');
    code_blocks.scrollTo({top: code_block.offsetTop, behavior: 'smooth'});

    // Send a message to the object frame to scroll to the line number.
    if(code.contentDocument && code.contentDocument.documentElement.innerText == "") {
        // If frame has not yet loaded...
        code.onload = function() {
            code.contentWindow.postMessage(line_num.toString(), "*");
        };
    } else {
        // If frame has loaded already...
        code.contentWindow.postMessage(line_num.toString(), "*");
    }
}

function hideCode(file_id) {
    // Hide the code block div.
    code_block = document.querySelector('#'+file_id);
    code_block.classList.replace('show', 'hide');

    // Clear the inner HTML of the object frame.
    code = code_block.querySelector('.code');
    if(code.contentDocument) {
        // If frame has already loaded, clear it.
        code.contentDocument.documentElement.innerHTML = "";
    }

    // If there are no more code blocks, hide the panel.
    code_blocks = document.querySelector('#code-blocks');
    if(code_blocks.querySelectorAll('.show').length <= 0) {
        // If no code blocks are left, close side panel.
        code_blocks.classList.replace('show', 'hide');
    }
}

// Reset All Log Blocks And Entries To Original State
function resetLogBlocks() {
    // Get all message and info log blocks.
    blocks = document.querySelectorAll('.log-block');
    blocks.forEach((block) => {
        log_entry = block.parentElement.parentElement;
        // Close the log block.
        if(block.classList.contains('info-block')) {
            btn = log_entry.querySelector('.info-btn > button');
            handleLogContent(btn, block.id, compress=true);
        } else if(block.classList.contains('msg-block')) {
            btn = log_entry.querySelector('.msg-btn > button');
            handleLogContent(btn, block.id, compress=true);
        }

        // Make background transparent in case it was highlighted by search.
        block.firstElementChild.style.backgroundColor = 'transparent';
    })

    // Hide all log entries and reset the exp btn for each entry.
    log_entries = document.querySelectorAll('.log-entry');
    log_entries.forEach((log_entry) => {
        item = log_entry.querySelector('.item-container');
        if(item){
            item.style.backgroundColor = 'initial';
        }
        exp_btn = log_entry.querySelector('.exp-btn');
        if(exp_btn) {
            exp_btn.classList.replace('show-logs', 'hide-logs');
            collapseLogs(log_entry);
        }
    })

    // Clear search results text.
    search_results = document.querySelector('#search-count');
    search_results.innerHTML = '';
}

// Regex Calculator
function searchRegex(text) {
    var wwo = document.querySelector('#search-whole-word');
    var regex = document.querySelector('#search-regex');
    var mc = document.querySelector('#search-match-case');

    // Prevent the text from inserting unwanted regex characters.
    var expr = regex.checked ? text : RegExp.escape(text);
    if(wwo.checked) {
        expr = `\\b${expr}\\b`;  // whole word only
    }
    var params = 'm';  // multi-line search option
    if(!mc.checked) {
        params += 'i';  // case insensitive
    }
    return new RegExp(expr, params);
}

// Process search request.
function processSearch(text, tag_toggled=false) {
    // Reset everything to reduce noise of search.
    resetLogBlocks();
    var include_msg_block = document.querySelector('#search-in-msg');
    var include_code_block = document.querySelector('#search-in-code');
    var include_info_block = document.querySelector('#search-in-info');
    var regex = searchRegex(text);
    var total_num_results = 0;  // Total searches found, but not necessarily shown.
    var shown_num_results = 0;  // Total searches shown.

    log_blocks = document.querySelectorAll('.log-block');
    // For every log block...
    for(var x=0; x < log_blocks.length; x++) {
        if(log_blocks[x].textContent.match(regex)) {
            // If a match occurs...
            total_num_results += 1;
            found = log_blocks[x];
            log_entry = found.parentElement.parentElement;
            if(include_info_block.checked && found.classList.contains('info-block')) {
                btn = log_entry.querySelector('.info-btn > button');
            } else if(include_msg_block.checked && found.classList.contains('msg-block')) {
                btn = log_entry.querySelector('.msg-btn > button');
            } else {
                continue;
            }
            if(log_entry.style.display !== 'none') {
                shown_num_results += 1;
                toggleShowHide(log_entry, hide=false);
            } else {
                continue;
            }

            // If the match has parent entries, expand them.
            cur_depth = Number(log_entry.getAttribute('aria-label'));  // Depth of match
            for(var j=log_entry.previousElementSibling; j !== null; j=j.previousElementSibling) {
                depth = Number(j.getAttribute('aria-label'));  // Depth of previous sibling
                if(depth < cur_depth) {
                    // The previous sibling is an ancestor
                    cur_depth = depth;
                    expandLogs(j);
                } else if (depth <= 0) {
                    break;  // No more ancestors. Stop looping.
                }
            }
            // Simulate a click to show the log block.
            handleLogContent(btn, found.id, compress=false);

            // Highlight the log block to show that it matched a search.
            found.firstElementChild.style.backgroundColor = 'rgba(0, 255, 0, 0.1)';
        }
    }

    // Display numbers of matched and shown entries of search.
    search_results = document.querySelector('#search-count');
    search_results.innerHTML = total_num_results + ' total results match "' + text + '".<br/>' + shown_num_results + ' results shown.';
}

// Search Log Entries By Message Blocks, Info Blocks, Whole-Word Only,
// Regular Expression, And/Or Match By Case.
function search(search_el_id, tag_toggled=false) {
    search_el = document.querySelector('#'+search_el_id);
    search_results = document.querySelector('#search-count');

    text = search_el.value;
    if(text.length == 0) {
        // Search text is empty.
        if(!tag_toggled) {
            // Don't ignore. Display message to type something.
            search_results.innerHTML = 'Type something to search.';
        }
        // Ignore.
        return;
    }

    // Call search engine.
    search_results.innerHTML = 'Searching...';
    setTimeout(function () { processSearch(text, tag_toggled); }, 120);
}

// Search When Input Has Focus And Enter Key Is Selected.
function searchOnEnter(event, search_el_id) {
    if(event.keyCode === 13) {
        search(search_el_id);
    }
}

// Expand Logs Matching A Log Tag
function expandByTag(tag_name, tag_toggled=false) {
    // Reset everything to reduce noise of search.
    resetLogBlocks();
    log_entries = document.querySelectorAll('.log-entry[aria-valuetext='+tag_name);
    var total_num_results = log_entries.length;  // Total searches found, but not necessarily shown.
    // For every log entry...
    for(var x=0; x < log_entries.length; x++) {
        log_entry = log_entries[x];
		exp_btn = log_entry.querySelector('.item-container');
        exp_btn.style.backgroundColor = 'var(--' + tag_name + ')';
        if(log_entry.style.display !== 'none') {
            toggleShowHide(log_entry, hide=false);
        } else {
            continue;
        }

        // If the match has parent entries, expand them.
        cur_depth = Number(log_entry.getAttribute('aria-label'));  // Depth of match
        for(var j=log_entry.previousElementSibling; j !== null; j=j.previousElementSibling) {
            depth = Number(j.getAttribute('aria-label'));  // Depth of previous sibling
            if(depth < cur_depth) {
                // The previous sibling is an ancestor
                cur_depth = depth;
                expandLogs(j);
            } else if (depth <= 0) {
                break;  // No more ancestors. Stop looping.
            }
        }
    }

    // Display numbers of shown entries of search.
    search_results = document.querySelector('#search-count');
    search_results.innerHTML = total_num_results + ' total results match "' + tag_name + '".';
}

// Hide/Show By Log Tag
function handleLogTagFilter(filter) {
    log_tag = filter.querySelector('input[type="checkbox"]');
    log_entries = document.querySelectorAll('.log-entry');
    display = log_tag.checked ? 'block' : 'none';
    triggered_depth = -1;
    triggered = false;
    log_entries.forEach((log_entry) => {
        var name = log_entry.getAttribute('aria-valuetext');  // This tag name.
        if(triggered) {
            var depth = log_entry.getAttribute('aria-label');  // This depth.
            if(Number(depth) > triggered_depth) {
                // If this depth is greater than the triggered depth, then it is a
                // descendant entry of the entry that was shown/hidden. So also
                // show/hide this, respectively.
                log_entry.style.display = display;
            } else {
                // This depth is less than the ancestor depth that triggered all child
                // logs to show/hide, so it is not affected. Lift the trigger.
                triggered = false;
            }
        }
        if(name !== null && name == log_tag.id) {
           // If this matches the log tag...
           log_entry.style.display = display;  // Show/Hide the entry.

           // Set trigger to indicate that all future siblings should be shown/hidden
           // until the depth matches this depth. This means all children entries of
           // an entry matching the log tag filter will be shown/hidden with its parent.
           if(!triggered) {
               triggered = true;
               triggered_depth = Number(log_entry.getAttribute('aria-label'));
           }
       }
    })
}
"""
PYTHON_CSS = """
/* Styles for Python code */
.highlight .hll { background-color: rgba(42, 213, 213, 0.2) }
.highlight .c { color: #408080; font-style: italic } /* Comment */
.highlight .err { border: 1px solid #FF0000 } /* Error */
.highlight .k { color: #008000; font-weight: bold } /* Keyword */
.highlight .o { color: #666666 } /* Operator */
.highlight .cm { color: #408080; font-style: italic } /* Comment.Multiline */
.highlight .cp { color: #BC7A00 } /* Comment.Preproc */
.highlight .c1 { color: #408080; font-style: italic } /* Comment.Single */
.highlight .cs { color: #408080; font-style: italic } /* Comment.Special */
.highlight .gd { color: #A00000 } /* Generic.Deleted */
.highlight .ge { font-style: italic } /* Generic.Emph */
.highlight .gr { color: #FF0000 } /* Generic.Error */
.highlight .gh { color: #000080; font-weight: bold } /* Generic.Heading */
.highlight .gi { color: #00A000 } /* Generic.Inserted */
.highlight .go { color: #808080 } /* Generic.Output */
.highlight .gp { color: #000080; font-weight: bold } /* Generic.Prompt */
.highlight .gs { font-weight: bold } /* Generic.Strong */
.highlight .gu { color: #800080; font-weight: bold } /* Generic.Subheading */
.highlight .gt { color: #0040D0 } /* Generic.Traceback */
.highlight .kc { color: #008000; font-weight: bold } /* Keyword.Constant */
.highlight .kd { color: #008000; font-weight: bold } /* Keyword.Declaration */
.highlight .kn { color: #008000; font-weight: bold } /* Keyword.Namespace */
.highlight .kp { color: #008000 } /* Keyword.Pseudo */
.highlight .kr { color: #008000; font-weight: bold } /* Keyword.Reserved */
.highlight .kt { color: #B00040 } /* Keyword.Type */
.highlight .m { color: #666666 } /* Literal.Number */
.highlight .s { color: #BA2121 } /* Literal.String */
.highlight .na { color: #7D9029 } /* Name.Attribute */
.highlight .nb { color: #008000 } /* Name.Builtin */
.highlight .nc { color: #0000FF; font-weight: bold } /* Name.Class */
.highlight .no { color: #880000 } /* Name.Constant */
.highlight .nd { color: #AA22FF } /* Name.Decorator */
.highlight .ni { color: #999999; font-weight: bold } /* Name.Entity */
.highlight .ne { color: #D2413A; font-weight: bold } /* Name.Exception */
.highlight .nf { color: #0000FF } /* Name.Function */
.highlight .nl { color: #A0A000 } /* Name.Label */
.highlight .nn { color: #0000FF; font-weight: bold } /* Name.Namespace */
.highlight .nt { color: #008000; font-weight: bold } /* Name.Tag */
.highlight .nv { color: #19177C } /* Name.Variable */
.highlight .ow { color: #AA22FF; font-weight: bold } /* Operator.Word */
.highlight .w { color: #bbbbbb } /* Text.Whitespace */
.highlight .mf { color: #666666 } /* Literal.Number.Float */
.highlight .mh { color: #666666 } /* Literal.Number.Hex */
.highlight .mi { color: #666666 } /* Literal.Number.Integer */
.highlight .mo { color: #666666 } /* Literal.Number.Oct */
.highlight .sb { color: #BA2121 } /* Literal.String.Backtick */
.highlight .sc { color: #BA2121 } /* Literal.String.Char */
.highlight .sd { color: #BA2121; font-style: italic } /* Literal.String.Doc */
.highlight .s2 { color: #BA2121 } /* Literal.String.Double */
.highlight .se { color: #BB6622; font-weight: bold } /* Literal.String.Escape */
.highlight .sh { color: #BA2121 } /* Literal.String.Heredoc */
.highlight .si { color: #BB6688; font-weight: bold } /* Literal.String.Interpol */
.highlight .sx { color: #008000 } /* Literal.String.Other */
.highlight .sr { color: #BB6688 } /* Literal.String.Regex */
.highlight .s1 { color: #BA2121 } /* Literal.String.Single */
.highlight .ss { color: #19177C } /* Literal.String.Symbol */
.highlight .bp { color: #008000 } /* Name.Builtin.Pseudo */
.highlight .vc { color: #19177C } /* Name.Variable.Class */
.highlight .vg { color: #19177C } /* Name.Variable.Global */
.highlight .vi { color: #19177C } /* Name.Variable.Instance */
.highlight .il { color: #666666 } /* Literal.Number.Integer.Long */
.highlight .filename { color: #444; font-style: italic } /* Filename */
"""
STYLES_CSS = """
body {
    width: 95vw;
    margin: auto;
    font-family: sans-serif;
    font-weight: normal;
}

button:focus, input:focus {
    outline:0;
}

input {
    border-radius: 10px;
    border: lightgrey outset 2px;
}

/* Custom Button Styles */
.btn {
    text-align: center;
    background-color: transparent;
    -webkit-transition : box-shadow 0.5s ease-out;
    -moz-transition : box-shadow 0.5s ease-out;
    -o-transition : box-shadow 0.5s ease-out;
    transition : box-shadow 0.5s ease-out;
}


.btn, .btn > * {
    cursor: pointer;
    background: white;
}

/* Show/Hide */
.decompressed {
    overflow: hidden;
    width: 100%;
    max-height: 1000px;
    transition: width .5s ease-in-out, max-height 0.7s ease-in-out;
    -moz-transition: width .5s ease-in-out, max-height 0.7s ease-in-out;
    -ms-transition: width .5s ease-in-out, max-height 0.7s ease-in-out;
    -o-transition: width .5s ease-in-out, max-height 0.7s ease-in-out;
    -webkit-transition: width .5s ease-in-out, max-height 0.7s ease-in-out;
}

.compressed {
    overflow: hidden;
    width: 0px;
    max-height: 0px;
    transition: width .5s ease-in-out, max-height 0.7s ease-in-out;
    -moz-transition: width .5s ease-in-out, max-height 0.7s ease-in-out;
    -ms-transition: width .5s ease-in-out, max-height 0.7s ease-in-out;
    -o-transition: width .5s ease-in-out, max-height 0.7s ease-in-out;
    -webkit-transition: width .5s ease-in-out, max-height 0.7s ease-in-out;
}

.show {
    display: block;
}

.hide {
    display: none !important;
}

.bold {
    font-weight: bold;
    color: green;
}

/* Divides Log Tags From Log Search Filters */
.divider {
    width: 80%;
    border-top: lightgrey solid 1px;
    margin: 15px auto;
}

/* Title And Legend */
#title {
    width: 100%;
    text-align: center;
    margin: 5px 0;
}

#legend {
    max-width: 100%;
    margin: 30px auto;
    display: grid;
}

#log-tags {
    display: grid;
    grid-template-columns: repeat(4, auto);
    grid-gap: 18px;
    justify-content: space-evenly;
    align-items: center;
    align-content: space-evenly;
    padding-top: 5px;
    padding-bottom: 25px;
}

#filters-container {
    display: block;
    margin: 1em 0;
}

.log-tag {
    display: inline-flex;
}

#filters-btn {
    min-width: 130px;
    min-height: 25px;
    border-radius: 10px;
    border: lightgrey solid 1px;
}

#filters-controls, #search-container {
    display: block;
    margin: 10px auto;
    width: max-content;
}

#search-params {
    display: grid;
    grid-template-columns: auto auto auto;
    grid-gap: 10px 20px;
}

#search-controls {
    border: lightgrey solid 2px;
    border-radius: 15px;
    width: max-content;
    margin: 30px auto 0 auto;
}

#search {
    width: 300px;
    line-height: 25px;
    padding: 0 15px;
    border: none;
}

#go-btn {
    height: 25px;
    border: lightgrey solid;
    border-width: 0 0 0 2px;
    padding-left: 15px;
    margin-right: 12px;
}

#search-count {
    text-align: center;
    font: 400 11px system-ui;
    margin-top: 10px;
    color: green;
    font-weight: bold;
    font-style: italic;
}

#filters-controls {
    padding-bottom: 10px;
}

#filters {
    border: lightgrey solid;
    border-width: 2px 0px;
    overflow: hidden;
    height: fit-content;
    margin: auto;
    padding: 15px 0;
}

#reset-btn {
    float: left;
    margin: 15px 0px;
    width: 80px;
    height: 25px;
    border-radius: 15px;
}

/* Code Block Frames */
#code-blocks {
    width: 50%;
    overflow: auto;
    margin: 0 15px;
    padding: 0 25px;
    float: right;
    border-left: lightgrey 1px ridge;
    position: -webkit-sticky;
    position: sticky;
    top: 0;
    max-height: 80vh;
}

object.code {
    width: 100%;
    height: 100%;
    border: none;
    margin: 0;
    padding: 0;
}

.code-block {
    margin: 10px;
    border: lightgrey 2px solid;
    border-radius: 5px;
}

.code-block-controls {
    position: sticky;
    top: 0;
    float: right;
    width: 100%;
    background-color: rgba(127, 127, 127);
    text-align: center;
    padding: 5px 0;
}

.close-code {
    background-color: darkred;
    color: white;
    float: right;
    margin-right: 10px;
    border-radius: 5px;
}

.code {
    padding: 10px;
    overflow: auto;
    margin: 0 10px;
    max-height: 400px;
}

.filepath {
    color: white;
    font-style: italic;
    display: inline-block;
    width: 93%;
    overflow: hidden;
    overflow-wrap: break-word;
}


/* Log Entries */
#log-entries {
    display: grid;
}

.log-entries {
    width: 100%;
    margin: auto;
}

.log-entry {
    height: fit-content;
    min-width: 80%;
}

.log-entry > .log-row {
    display: grid;
        grid-template-columns: 35px 300px auto repeat(var(--log-entry-btns), minmax(auto, 80px));
}

.log-row {
    margin: 3px 0;
}

.log-row > div {
    padding: 0px 3px;
}

.item-container {
    border-right: lightgrey solid 2px;
}

.item-container > button {
    border: none;
    background: transparent;
}

.func {
    text-align: left;
    padding: 0px 15px !important;
    overflow: hidden;
    text-overflow: ellipsis;
}

.preview {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    text-indent: 13px;
}

.exp-btn::before {
    position: relative;
    top: 3pt;
    left: 2pt;
    content: "";
    display: inline-block;
    width: 0.4em;
    height: 0.4em;
    border-right: 0.2em solid black;
    border-top: 0.2em solid black;
}

.exp-btn:hover::before {
    border-color: green;
}

.hide-logs::before {
    transform: rotate(45deg);
    margin-right: 0.5em;
    transition: transform 0.8s;
    -moz-transition: transform 0.3s;
    -ms-transition: transform 0.3s;
    -o-transition: transform 0.3s;
    -webkit-transition: transform 0.3s;
}

.show-logs::before {
    transform: rotate(135deg);
    margin-right: 0.5em;
    transition: transform 0.3s;
    -moz-transition: transform 0.3s;
    -ms-transition: transform 0.3s;
    -o-transition: transform 0.3s;
    -webkit-transition: transform 0.3s;
}

.no-exp {
    opacity: 0.5;
    text-align: center;
    cursor: default;
}

.log-block > pre, .log-block > div {
    border: lightgrey solid 2px;
    margin: 2px auto;
    border-radius: 10px;
    padding: 15px;
    overflow: auto;
    max-height: 400px !important;
    white-space: pre-wrap;
    overflow-wrap: break-word;
}

.log-block-container {
    margin: auto;
    padding: 0 10px;
}

/* Switch Toggle */
.fancy-checkbox {
    display: grid;
    grid-template-columns: auto auto auto;
    grid-gap: 10px;
    justify-content: start;
}

.switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 16px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  -webkit-transition: .4s;
  transition: .4s;
}

.slider:before {
  position: absolute;
  content: "";
  height: 13px;
  width: 13px;
  left: 2px;
  bottom: 2px;
  background-color: white;
  -webkit-transition: .4s;
  transition: .4s;
}

input:not(:checked) + .slider {
    background-color: #ccc !important;
}

input:checked + .slider {
  background-color: #2196F3;
}

input:focus + .slider {
  box-shadow: 0 0 1px #2196F3;
}

input:checked + .slider:before {
  -webkit-transform: translateX(26px);
  -ms-transform: translateX(26px);
  transform: translateX(26px);
}

/* Rounded sliders */
.slider.round {
  border-radius: 34px;
}

.slider.round:before {
  border-radius: 50%;
}
"""

class HtmlLogGenerator:
    def __init__(self):
        self._sql = None  # type: Optional[LoggerSql]

    def generate(self, log_file: Union[str, Path], title: str = None, include_code: bool = True,
                 datetime_range: Tuple[datetime, datetime] = None, exclude_files: List[str] = None,
                 db_file: Union[str, Path] = None):
        """
        Generates an HTML file that display logs persisted by the logger in the SQLite DB. Consider the
        parameter definitions for ways to reduce the size of the output and control the content in the
        output.

        Args:
            log_file: Absolute path to the SQLite DB log file.
            title: Title of the log file. Default is "Log File".
            include_code: If ``False``, then the code blocks are not included in the output file. This
                          is desirable when trying to save space in the output and/or excluding all
                          files for security purposes. If code blocks are not included, an Info block
                          is still included in each log entry that displays the file name and line number
                          of where the log message was recorded.
            datetime_range: Defines the start and/or end date parameters of the log data included in the
                            output file. This is always a ``Tuple`` of size 2 where the first item is the
                            start date and the second is the end date. If only a start or end date is
                            desired, then set the other value to ``None``. Date should be ``datetime``
                            objects.
            exclude_files: A list of regular expressions for files that should NOT be included in the
                           code blocks. If ``include_code=True``, then the code files are included in
                           the output so the code can be referenced directly by the logs. This parameter
                           can be used to improve security and space. It is recommended to exclude files
                           that may leak sensitive information and are highly unlikely to provide much
                           use to the log file.
            db_file: Location of the .db file. If not given, it is assumed to be in the same path as the log_file.
        """
        # region Get Content Of Log File
        if not isinstance(log_file, Path):
            log_file = Path(log_file)
        db_file = db_file or log_file
        self._sql = LoggerSql(db_file)
        # endregion Get Content Of Log File

        # region Create HTML File
        log_tags = self._get_log_tags()

        log_entries_query = f'select * from {self._sql.log_entries.table_name}'
        if isinstance(datetime_range, (tuple, list)):
            if not len(datetime_range) == 2:
                raise ValueError(f'Datetime range must be a Tuple object of size 2 where the first '
                                 f'element, a datetime object, represents the "from" date and the '
                                 f'second, also a datetime object, represents the "to" date. To omit '
                                 f'one or the other, set the value to None.')
            dt_fmt = lambda x: x.strftime('%Y-%m-%d %H:%M:%S')
            if start := datetime_range[0]:
                if end := datetime_range[1]:
                    log_entries_query += f" where timestamp between '{dt_fmt(start)}' and '{dt_fmt(end)}'"
                else:
                    log_entries_query += f" where timestamp >= '{dt_fmt(start)}'"
            elif end := datetime_range[1]:
                log_entries_query += f" where timestamp <= '{dt_fmt(end)}'"
        log_entries = self._sql.select(query=log_entries_query)

        title = title or 'Log Results'
        code_blocks = self._get_code_blocks(log_entries=log_entries,
                                            exclude_files=exclude_files) if include_code else None
        # Minify HTML file to reduce space.
        html = htmlmin.minify(f"""
        <html>
            <head>
                <title>{title}</title>
                <script type="text/javascript">
                    {ACTION_JS}
                </script>
                <style>
                    {STYLES_CSS}
                    {self._get_styles(log_tags=log_tags, include_code=include_code)}
                </style>
            </head>
            <body>
                <!-- Title -->
                <div id="title">
                    <h1>{title}</h1>
                </div>
                <!-- Legend -->
                <div id="legend">
                    {self._legend(log_tags=log_tags)}
                </div>
                <!-- Code Blocks -->
                <div class="hide" id="code-blocks">
                    {''.join([cb['block'] for cb in code_blocks.values()]) if code_blocks else ''}
                </div>
                <!-- Log Entries -->
                <div id="log-entries">
                    {self._get_log_entries(log_tags=log_tags, log_entries=log_entries,
                                           code_blocks=code_blocks if include_code else None)}
                </div>
            </body>
            {'<br/>' * 12}
        </html>
        """, remove_comments=True, remove_empty_space=True)
        # endregion Create HTML File

        # region Send Files To Log Directory
        resources = f'{log_file.parent}'
        file_path = ''
        for part in resources.split(os.sep):
            file_path += part + os.sep
            if not os.path.exists(file_path):
                os.mkdir(file_path)

        if code_blocks:
            for values in code_blocks.values():
                with open(f"{resources}/{values['path']}", 'w') as f:
                    f.write(values['code'])

        print(f'Writing the HTML file here: {log_file.parent.absolute()}/{log_file.stem}.html')
        with open(f'{log_file.parent.absolute()}/{log_file.stem}.html', 'w') as f:
            f.write(html)
        # endregion Send Files To Log Directory

    def _get_log_tags(self):
        log_tags = self._sql.select(
            query=f'select * from {self._sql.log_tags.table_name}'
        )
        return {
            tag[self._sql.log_tags.name]: LogTag(
                name=tag[self._sql.log_tags.name],
                value=tag[self._sql.log_tags.value],
                html_color=tag[self._sql.log_tags.color]
            )
            for tag in log_tags.iterate()
        }

    @staticmethod
    def _get_styles(log_tags: Dict[str, LogTag], include_code: bool):
        """
        Sets the global dynamic style variables and classes. These styles cannot be controlled
        by a stylesheet because they are dynamically created based on the log tags.
        """
        colors = []
        classes = []
        for ll in log_tags.values():
            colors.append(f'--{ll.alias}: {ll.html_color};')  # Color of log tag.
            # Each log tag has its own style class for highlighting the bottom of the
            # log entry.
            classes.append(f"""
            .{ll.alias} {{
                border-left: var(--{ll.alias}) solid 5px;
                border-bottom: lightgrey solid 2px;
                transition: border-bottom 0.2s ease-in-out;
            }}

            .{ll.alias}:hover {{
                border-bottom: var(--{ll.alias}) solid 2px;

            }}
            """)
        colors = '\n\t'.join(colors)
        classes = '\n'.join(classes)
        # Send the style classes along with a variable that sets the number of log entry buttons
        # to show. The "Code" button can be omitted.
        return f"""
        :root {{
            {colors}
            --log-entry-btns: {3 if include_code else 2}
        }}

        {classes}
        """

    @staticmethod
    def _legend(log_tags: Dict[str, LogTag]):
        """
        Sets the log tags and the search filters in the legend.
        """

        def add_filter(log_tag: LogTag):
            return f"""
            <div class="log-tag fancy-checkbox" 
                 aria-label="{log_tag.alias}" 
                 aria-valuetext="{log_tag.value}"
                 onclick="handleLogTagFilter(this)">
                <label class="switch">
                    <input id="{log_tag.alias}" type="checkbox" checked>
                    <span 
                        class="slider round" 
                        style="background-color: {log_tag.html_color}; box-shadow: 0 0 10px {log_tag.html_color};">
                    </span>
                </label>
                <span>{log_tag.name}</span>
                <button id="{log_tag.alias}" class="btn" onclick="expandByTag(this.id)">Show</button>
            </div>
            """

        filters = '\n'.join([
            add_filter(log_tag=log_tag)
            for log_tag in log_tags.values()
        ])
        return f"""
        <div id="filters-container">
            <div id="filters-controls">
                <button id="filters-btn" class="btn" onclick="handleShowFilter(this)">Hide Filters</button>
            </div>
            <div id="filters-wrapper">
                <div id="filters" class="decompressed">
                    <div id="log-tags">
                        {filters}
                    </div>
                    <div class="divider"></div>
                    <div id="search-container">
                        <div id="search-params">
                            <div class="search-param fancy-checkbox">
                                <label class="switch">
                                    <input id="search-in-msg" type="checkbox" checked>
                                    <span class="slider round"></span>
                                </label>
                                <span>Include Message Blocks</span>
                            </div>
                            <div class="search-param fancy-checkbox">
                                <label class="switch">
                                    <input id="search-in-info" type="checkbox" checked>
                                    <span class="slider round"></span>
                                </label>
                                <span>Include Info Blocks</span>
                            </div>
                            <div></div>
                            <div class="search-param fancy-checkbox">
                                <label class="switch">
                                    <input id="search-whole-word" type="checkbox">
                                    <span class="slider round"></span>
                                </label>
                                <span>Whole Word Only</span>
                            </div>
                            <div class="search-param fancy-checkbox">
                                <label class="switch">
                                    <input id="search-regex" type="checkbox">
                                    <span class="slider round"></span>
                                </label>
                                <span>Use Regular Expression</span>
                            </div>
                            <div class="search-param fancy-checkbox">
                                <label class="switch">
                                    <input id="search-match-case" type="checkbox">
                                    <span class="slider round"></span>
                                </label>
                                <span>Match Case</span>
                            </div>
                        </div>
                        <div id="search-controls">
                            <input id="search" type="text" placeholder="Search for text..." onkeyup="searchOnEnter(event, this.id)">
                            <button id="go-btn" class="btn" onclick="search('search')">Go</button>
                        </div>
                        <div id="search-count"></div>
                    </div>
                </div>
            </div>
        </div>
        """

    def _get_code_blocks(self, log_entries: SelectResult, exclude_files: List[str] = None):
        """
        Creates the code block panel, code block object tags, and the file name for each block.
        The object tag uses a function to send a line number to scroll to when the frame is opened.
        """
        exclude_files = exclude_files or []
        cols = self._sql.log_entries
        codes = {}  # type: Dict
        fc = 0
        if exclude_files:
            exclude_regexes = "(" + ")|(".join(exclude_files) + ")"
        else:
            exclude_regexes = None
        for le in list(log_entries.iterate()):
            fp = le[cols.file_path]
            if fp not in codes.keys():
                if exclude_regexes and re.match(pattern=exclude_regexes, string=fp, flags=re.IGNORECASE):
                    continue
                with open(fp, 'r') as f:
                    code = f.read()
                code_html = highlight(
                    code=code,
                    lexer=PythonLexer(),
                    formatter=HtmlFormatter(linenos='inline')
                )
                fc += 1
                file_id = f"file-id-{fc}"
                # Minify to reduce space.
                code = htmlmin.minify(f"""
                <html>
                    <head>
                        <script>
                            window.addEventListener("message", function(event) {{
                                line_num = Number(event.data);
                                view_line = line_num > 2 ? line_num - 3 : 0;
                                linenos = document.querySelectorAll('.lineno');
                                if(linenos.length > 0) {{
                                    linenos.forEach(line => {{line.style.backgroundColor = 'transparent';}})
                                    linenos[line_num - 1].style.backgroundColor = 'lightgreen';
                                    body = document.querySelector('body');
                                    body.scrollTo({{top: linenos[view_line].offsetTop, behavior: 'smooth'}});
                                }}
                            }})
                        </script>
                        <style>
                            {PYTHON_CSS}
                        </style>
                    </head>
                    <body>
                        {code_html}
                    </body>
                </html>
                """, remove_empty_space=True)
                # A UUID is used on the filename to create a consistent but unique filename for the HTML file
                # for the code. This prevents clashing of filenames.
                path = f'{uuid.uuid3(uuid.NAMESPACE_OID, fp).hex}.html'
                codes[fp] = {
                    'id'   : file_id,
                    'path' : path,
                    'block': f'''
                        <div class="code-block hide" id="{file_id}" aria-label="{Path(fp).stem}.html">
                            <div class="code-block-controls">
                                <span class="filepath" title="{le[cols.file_path]}">{le[cols.file_path]}</span>
                                <button class="close-code" onclick="hideCode('{file_id}')">X</button>
                            </div>
                            <div>
                                <object class="code" data="./{path}" type="text/html"></object>
                            </div>
                        </div>
                    ''',
                    'code' : code
                }
        return codes

    def _get_log_entries(self, log_tags: Dict[str, LogTag], log_entries: SelectResult,
                               code_blocks: Dict[str, Dict[str, str]]):
        """
        Creates the reset button, log entries, and log blocks.
        """
        cols = self._sql.log_entries

        def format_info_block(le: dict):
            return f'File: {le[cols.file_path]}\n' \
                   f'Line Number: {le[cols.line_num]}\n' \
                   f'Qualified Name: {le[cols.function_name]}\n' \
                   f'Thread Id: {le[cols.thread_id]}\n' \
                   f'Thread Name: {le[cols.thread_name]}\n' \
                   f'Timestamp: {le[cols.timestamp]}\n' \
                   f'Log Tag: {le[cols.tag_name]}'

        logs = [
            f"""
            <div id="log-entries-controls">
                <div class="btn">
                    <button id="reset-btn" onclick="resetLogBlocks()">Reset</button>
                </div>
            </div>
            """
        ]

        def organize(les: List[dict]):
            """
            Organizes the log entries by thread and timestamp.
            """
            entries = []
            threads = {}
            for le in sorted(les, key=lambda x: x['id']):
                thread_name = le[cols.thread_name]
                if bool(le[cols.is_main_thread]):
                    entries.append(le)
                elif thread_name not in entries:
                    entries.append(thread_name)
                    threads[thread_name] = [le]
                else:
                    threads[thread_name].append(le)

            results = []
            for entry in entries:
                if isinstance(entry, dict):
                    results.append(entry)
                else:
                    results.extend(threads[entry])
            return results

        log_entries = organize(les=list(log_entries.iterate()).copy())

        for e, log_entry in enumerate(log_entries):
            log_tag = log_tags[log_entry[cols.tag_name]]
            log_entry_id = f'log-entry-{e}'
            msg_block_id = f'msg-block-{e}'
            info_block_id = f'info-block-{e}'

            display = "hide" if log_entry[cols.depth] > 0 else "show"
            # Only show exp btn if there are child entries to this entry.
            if e < (len(log_entries) - 1) and \
                    log_entries[e + 1][cols.depth] > log_entry[cols.depth]:
                expand_btn = f"""
                <div class="btn item-container">
                    <button class="exp-btn hide-logs" onclick="toggleExpLogs('{log_entry_id}')"></button>
                </div>
                """
            else:
                expand_btn = f"""
                <div class="item-container">
                    <div class="no-exp">-</div>
                </div>
                """
            # Only show the code block button if enabled.
            if code_blocks:
                code_block = code_blocks.get(log_entry[cols.file_path])
                fid, fp = code_block.get('id'), code_block.get('path')
                code_btn = f'''
                    <div class="code-btn btn item-container">
                        <button onclick="showCode('{fid}', '{fp}', {log_entry[cols.line_num]})">Code</button>
                    </div>
                '''
            else:
                code_btn = ''
            func_def = f'{log_entry[cols.function_name]}:{log_entry[cols.line_num]}'
            logs.append(f"""
            <div id='{log_entry_id}' 
                 class="log-entry {display}"
                 aria-valuetext="{log_tag.alias}" 
                 aria-label="{log_entry[cols.depth]}">
                <div class="log-row {log_tag.alias}" style="margin-left: {log_entry[cols.depth] * 25}px;">
                    {expand_btn}
                    <div class="func item-container">
                        <span title="{func_def}">{func_def}</span>
                    </div>
                    <div class="preview item-container">
                        <span>{log_entry[cols.msg]}</span>
                    </div>
                    <div class="msg-btn btn item-container">
                        <button onclick="handleLogContent(this, '{msg_block_id}')">Message</button>
                    </div>
                    <div class="info-btn btn item-container">
                        <button onclick="handleLogContent(this, '{info_block_id}')">Info</button>
                    </div>
                    {code_btn}
                </div>
                <div 
                    class="log-block-container" 
                    style="border-left: var(--{log_tag.alias}) solid 5px; margin-left: {log_entry[cols.depth] * 25}px;"
                >
                    <div id="info-block-{e}" class="info-block log-block hide">
                        <pre>{format_info_block(log_entry)}</pre>
                    </div>
                    <div id="msg-block-{e}" class="msg-block log-block hide">
                        <pre>{log_entry[cols.msg]}</pre>
                    </div>
                </div>
            </div>
            """)
            e += 1
        return ''.join(logs)
