# Resource object code (Python 3)
# Created by: object code
# Created by: The Resource Compiler for Qt version 5.15.2
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore

qt_resource_data = b"\
\x00\x00\x08\x8d\
/\
*\x0a * libstored, \
distributed debu\
ggable data stor\
es.\x0a * Copyright\
 (C) 2020-2021  \
Jochem Rutgers\x0a \
*\x0a * This progra\
m is free softwa\
re: you can redi\
stribute it and/\
or modify\x0a * it \
under the terms \
of the GNU Lesse\
r General Public\
 License as publ\
ished by\x0a * the \
Free Software Fo\
undation, either\
 version 3 of th\
e License, or\x0a *\
 (at your option\
) any later vers\
ion.\x0a *\x0a * This \
program is distr\
ibuted in the ho\
pe that it will \
be useful,\x0a * bu\
t WITHOUT ANY WA\
RRANTY; without \
even the implied\
 warranty of\x0a * \
MERCHANTABILITY \
or FITNESS FOR A\
 PARTICULAR PURP\
OSE.  See the\x0a *\
 GNU Lesser Gene\
ral Public Licen\
se for more deta\
ils.\x0a *\x0a * You s\
hould have recei\
ved a copy of th\
e GNU Lesser Gen\
eral Public Lice\
nse\x0a * along wit\
h this program. \
 If not, see <ht\
tps://www.gnu.or\
g/licenses/>.\x0a *\
/\x0a\x0aimport QtQuic\
k 2.12\x0aimport Qt\
Quick.Layouts 1.\
15\x0aimport QtQuic\
k.Window 2.2\x0aimp\
ort QtQuick.Cont\
rols 2.5\x0a\x0aWindow\
 {\x0a\x0a    id: root\
\x0a    visible: tr\
ue\x0a    width: 40\
0\x0a    height: 30\
0\x0a\x0a    readonly \
property int fon\
tSize: 10\x0a\x0a    C\
omponent.onCompl\
eted: {\x0a        \
var text = \x22Visu\
\x22\x0a\x0a        var i\
d = client.ident\
ification()\x0a    \
    if(id && id \
!== \x22?\x22)\x0a       \
 {\x0a            t\
ext += \x22: \x22 + id\
\x0a\x0a            va\
r v = client.ver\
sion()\x0a         \
   if(v && v !==\
 \x22?\x22)\x0a          \
      text += \x22 \
(\x22 + v + \x22)\x22\x0a   \
     }\x0a\x0a        \
root.title = tex\
t\x0a    }\x0a\x0a    Col\
umnLayout {\x0a    \
    anchors.fill\
: parent\x0a       \
 anchors.margins\
: 5\x0a\x0a        Tex\
tField {\x0a       \
     id: req\x0a   \
         Layout.\
preferredHeight:\
 root.fontSize *\
 2\x0a            f\
ont.pixelSize: r\
oot.fontSize\x0a   \
         Layout.\
fillWidth: true\x0a\
            plac\
eholderText: \x22en\
ter command\x22\x0a   \
         backgro\
und.antialiasing\
: true\x0a         \
   topPadding: 0\
\x0a            bot\
tomPadding: 0\x0a\x0a \
           onAcc\
epted: {\x0a       \
         rep.tex\
t = client.req(t\
ext)\x0a           \
 }\x0a        }\x0a\x0a  \
      ScrollView\
 {\x0a            L\
ayout.fillWidth:\
 true\x0a          \
  Layout.fillHei\
ght: true\x0a      \
      clip: true\
\x0a\x0a            Te\
xtArea {\x0a       \
         id: rep\
\x0a               \
 readOnly: true\x0a\
                \
font.pixelSize: \
root.fontSize\x0a  \
          }\x0a\x0a   \
         backgro\
und: Rectangle {\
\x0a               \
 antialiasing: t\
rue\x0a            \
    border.color\
: \x22#c0c0c0\x22\x0a    \
        }\x0a      \
  }\x0a    }\x0a}\x0a\
\x00\x00\x06\xe1\
/\
*\x0a * libstored, \
distributed debu\
ggable data stor\
es.\x0a * Copyright\
 (C) 2020-2021  \
Jochem Rutgers\x0a \
*\x0a * This progra\
m is free softwa\
re: you can redi\
stribute it and/\
or modify\x0a * it \
under the terms \
of the GNU Lesse\
r General Public\
 License as publ\
ished by\x0a * the \
Free Software Fo\
undation, either\
 version 3 of th\
e License, or\x0a *\
 (at your option\
) any later vers\
ion.\x0a *\x0a * This \
program is distr\
ibuted in the ho\
pe that it will \
be useful,\x0a * bu\
t WITHOUT ANY WA\
RRANTY; without \
even the implied\
 warranty of\x0a * \
MERCHANTABILITY \
or FITNESS FOR A\
 PARTICULAR PURP\
OSE.  See the\x0a *\
 GNU Lesser Gene\
ral Public Licen\
se for more deta\
ils.\x0a *\x0a * You s\
hould have recei\
ved a copy of th\
e GNU Lesser Gen\
eral Public Lice\
nse\x0a * along wit\
h this program. \
 If not, see <ht\
tps://www.gnu.or\
g/licenses/>.\x0a *\
/\x0a\x0aimport QtQuic\
k.Controls 2.12\x0a\
import QtQuick 2\
.12\x0a\x0aMeasurement\
 {\x0a    readOnly:\
 false\x0a    pollI\
nterval: 0\x0a\x0a    \
property bool ed\
iting: activeFoc\
us && displayTex\
t != valueFormat\
ted\x0a\x0a    propert\
y bool _edited: \
false\x0a    onEdit\
ingChanged : {\x0a \
       if(!editi\
ng) {\x0a          \
  _edited = true\
\x0a            Qt.\
callLater(functi\
on() { _edited: \
false })\x0a       \
 }\x0a    }\x0a\x0a    pr\
operty bool vali\
d: true\x0a    prop\
erty color valid\
BackgroundColor:\
 \x22white\x22\x0a    pro\
perty color inva\
lidBackgroundCol\
or: \x22#ffe0e0\x22\x0a  \
  palette.base: \
valid ? validBac\
kgroundColor : i\
nvalidBackground\
Color\x0a\x0a    color\
: editing ? \x22red\
\x22 : !connected ?\
 \x22gray\x22 : refres\
hed && !_edited \
? \x22blue\x22 : \x22blac\
k\x22\x0a    text: \x22\x22\x0a\
\x0a    onAccepted:\
 {\x0a        o.set\
(displayText)\x0a  \
      Qt.callLat\
er(function() { \
text = valueForm\
atted })\x0a    }\x0a\x0a\
    onActiveFocu\
sChanged: {\x0a    \
    if(activeFoc\
us)\x0a            \
text = valueForm\
atted\x0a        el\
se\x0a            t\
ext = _text\x0a    \
}\x0a\x0a    on_TextCh\
anged: {\x0a       \
 if(!editing)\x0a  \
          text =\
 _text\x0a    }\x0a}\x0a\x0a\
\
\x00\x00\x07\xe8\
/\
*\x0a * libstored, \
distributed debu\
ggable data stor\
es.\x0a * Copyright\
 (C) 2020-2021  \
Jochem Rutgers\x0a \
*\x0a * This progra\
m is free softwa\
re: you can redi\
stribute it and/\
or modify\x0a * it \
under the terms \
of the GNU Lesse\
r General Public\
 License as publ\
ished by\x0a * the \
Free Software Fo\
undation, either\
 version 3 of th\
e License, or\x0a *\
 (at your option\
) any later vers\
ion.\x0a *\x0a * This \
program is distr\
ibuted in the ho\
pe that it will \
be useful,\x0a * bu\
t WITHOUT ANY WA\
RRANTY; without \
even the implied\
 warranty of\x0a * \
MERCHANTABILITY \
or FITNESS FOR A\
 PARTICULAR PURP\
OSE.  See the\x0a *\
 GNU Lesser Gene\
ral Public Licen\
se for more deta\
ils.\x0a *\x0a * You s\
hould have recei\
ved a copy of th\
e GNU Lesser Gen\
eral Public Lice\
nse\x0a * along wit\
h this program. \
 If not, see <ht\
tps://www.gnu.or\
g/licenses/>.\x0a *\
/\x0a\x0aimport QtQuic\
k.Controls 2.12\x0a\
import QtQuick 2\
.12\x0a\x0aTextField {\
\x0a    id: comp\x0a\x0a \
   background.an\
tialiasing: true\
\x0a\x0a    topPadding\
: 0\x0a    bottomPa\
dding: 0\x0a    lef\
tPadding: 0\x0a    \
horizontalAlignm\
ent: TextInput.A\
lignRight\x0a    re\
adOnly: true\x0a\x0a  \
  property strin\
g unit: ''\x0a\x0a    \
property alias r\
ef: o.ref\x0a    pr\
operty alias obj\
: o.obj\x0a    prop\
erty alias pollI\
nterval: o.pollI\
nterval\x0a    prop\
erty alias refre\
shed: o.refreshe\
d\x0a    property a\
lias value: o.va\
lue\x0a    property\
 bool connected:\
 o.obj !== null\x0a\
\x0a    property va\
r o: StoreObject\
 {\x0a        id: o\
\x0a    }\x0a\x0a    // S\
pecify a (lambda\
) function, whic\
h will be used t\
o convert the va\
lue\x0a    // to a \
string. If null,\
 the valueString\
 of the object i\
s used.\x0a    prop\
erty var formatt\
er: null\x0a\x0a    pr\
operty string va\
lueFormatted: {\x0a\
        var s;\x0a\x0a\
        if(!conn\
ected)\x0a         \
   s = '';\x0a     \
   else if(forma\
tter)\x0a          \
  s = formatter(\
o.value);\x0a      \
  else\x0a         \
   s = o.valueSt\
ring;\x0a\x0a        r\
eturn s\x0a    }\x0a\x0a \
   property stri\
ng _text: {\x0a    \
    var s = '';\x0a\
        if(!conn\
ected)\x0a         \
   s = '?';\x0a    \
    else\x0a       \
     s = valueFo\
rmatted;\x0a\x0a      \
  if(unit != '')\
\x0a            s +\
= ' ' + unit\x0a\x0a  \
      return s\x0a \
   }\x0a    text: _\
text\x0a\x0a    color:\
 !connected ? \x22g\
ray\x22 : refreshed\
 ? \x22blue\x22 : \x22bla\
ck\x22\x0a}\x0a\x0a\
\x00\x00\x08O\
/\
*\x0a * libstored, \
distributed debu\
ggable data stor\
es.\x0a * Copyright\
 (C) 2020-2021  \
Jochem Rutgers\x0a \
*\x0a * This progra\
m is free softwa\
re: you can redi\
stribute it and/\
or modify\x0a * it \
under the terms \
of the GNU Lesse\
r General Public\
 License as publ\
ished by\x0a * the \
Free Software Fo\
undation, either\
 version 3 of th\
e License, or\x0a *\
 (at your option\
) any later vers\
ion.\x0a *\x0a * This \
program is distr\
ibuted in the ho\
pe that it will \
be useful,\x0a * bu\
t WITHOUT ANY WA\
RRANTY; without \
even the implied\
 warranty of\x0a * \
MERCHANTABILITY \
or FITNESS FOR A\
 PARTICULAR PURP\
OSE.  See the\x0a *\
 GNU Lesser Gene\
ral Public Licen\
se for more deta\
ils.\x0a *\x0a * You s\
hould have recei\
ved a copy of th\
e GNU Lesser Gen\
eral Public Lice\
nse\x0a * along wit\
h this program. \
 If not, see <ht\
tps://www.gnu.or\
g/licenses/>.\x0a *\
/\x0a\x0aimport QtQuic\
k 2.12\x0a\x0aItem {\x0a \
   id: comp\x0a\x0a   \
 required proper\
ty var ref\x0a    p\
roperty var obj:\
 null\x0a    proper\
ty string name: \
obj ? obj.name :\
 \x22\x22\x0a    property\
 real pollInterv\
al: 2\x0a\x0a    onRef\
Changed: {\x0a     \
   if(typeof(ref\
) != \x22string\x22) {\
\x0a            obj\
 = ref\x0a        }\
 else if(typeof(\
client) == \x22unde\
fined\x22) {\x0a      \
      obj = null\
\x0a        } else \
{\x0a            ob\
j = client.obj(r\
ef)\x0a        }\x0a  \
  }\x0a\x0a    onObjCh\
anged: {\x0a       \
 if(obj) {\x0a     \
       value = o\
bj.value\x0a\x0a      \
      if(!obj.po\
lling) {\x0a       \
         if(poll\
Interval > 0)\x0a  \
                \
  obj.poll(pollI\
nterval)\x0a       \
         else\x0a  \
                \
  obj.asyncRead(\
)\x0a            } \
else if(pollInte\
rval > 0 && obj.\
pollInterval > p\
ollInterval) {\x0a \
               /\
/ Prefer the fas\
ter setting, if \
there are multip\
le.\x0a            \
    obj.poll(pol\
lInterval)\x0a     \
       }\x0a       \
 } else {\x0a      \
      value = nu\
ll\x0a        }\x0a   \
 }\x0a\x0a    property\
 string valueStr\
ing: obj ? obj.v\
alueString : ''\x0a\
    property var\
 value: null\x0a\x0a  \
  property bool \
refreshed: false\
\x0a\x0a    Timer {\x0a  \
      id: update\
dTimer\x0a        i\
nterval: 1100\x0a  \
      onTriggere\
d: comp.refreshe\
d = false\x0a    }\x0a\
\x0a    onValueStri\
ngChanged: {\x0a   \
     if(obj)\x0a   \
         value =\
 obj.value\x0a\x0a    \
    comp.refresh\
ed = true\x0a      \
  updatedTimer.r\
estart()\x0a    }\x0a\x0a\
    function set\
(x) {\x0a        if\
(obj)\x0a          \
  obj.valueStrin\
g = x\x0a    }\x0a}\x0a\
\x00\x00\x00f\
m\
odule Components\
\x0aInput 1.0 Input\
.qml\x0aMeasurement\
 1.0 Measurement\
.qml\x0aStoreObject\
 1.0 StoreObject\
.qml\x0a\
"

qt_resource_name = b"\
\x00\x09\
\x09\xab\x8dT\
\x00l\
\x00i\x00b\x00s\x00t\x00o\x00r\x00e\x00d\
\x00\x08\
\x08\x01Z\x5c\
\x00m\
\x00a\x00i\x00n\x00.\x00q\x00m\x00l\
\x00\x0a\
\x07n\x093\
\x00C\
\x00o\x00m\x00p\x00o\x00n\x00e\x00n\x00t\x00s\
\x00\x09\
\x07\xc7\xf8\x9c\
\x00I\
\x00n\x00p\x00u\x00t\x00.\x00q\x00m\x00l\
\x00\x0f\
\x0d\x0f\x0a\xbc\
\x00M\
\x00e\x00a\x00s\x00u\x00r\x00e\x00m\x00e\x00n\x00t\x00.\x00q\x00m\x00l\
\x00\x0f\
\x06\xb2\x90\xfc\
\x00S\
\x00t\x00o\x00r\x00e\x00O\x00b\x00j\x00e\x00c\x00t\x00.\x00q\x00m\x00l\
\x00\x06\
\x07\x84+\x02\
\x00q\
\x00m\x00l\x00d\x00i\x00r\
"

qt_resource_struct = b"\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x02\x00\x00\x00\x01\
\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x18\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\
\x00\x00\x01{z[\xc0~\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x03\
\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00.\x00\x02\x00\x00\x00\x04\x00\x00\x00\x04\
\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x84\x00\x00\x00\x00\x00\x01\x00\x00\x17b\
\x00\x00\x01{z[\xc0|\
\x00\x00\x00\xa8\x00\x00\x00\x00\x00\x01\x00\x00\x1f\xb5\
\x00\x00\x01{z[\xc0|\
\x00\x00\x00H\x00\x00\x00\x00\x00\x01\x00\x00\x08\x91\
\x00\x00\x01{z[\xc0|\
\x00\x00\x00`\x00\x00\x00\x00\x00\x01\x00\x00\x0fv\
\x00\x00\x01{z[\xc0|\
"

def qInitResources():
    QtCore.qRegisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

def qCleanupResources():
    QtCore.qUnregisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

qInitResources()
