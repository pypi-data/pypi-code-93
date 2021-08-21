#   Copyright 2021 Geographs
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
ASCII = """\u001b[36m      ::::::::  ::::    ::: :::::::::: ::::::::  ::::    ::: ::::::::::: :::::::::  :::::::::: 
    :+:    :+: :+:+:   :+: :+:       :+:    :+: :+:+:   :+:     :+:     :+:    :+: :+:         
   +:+    +:+ :+:+:+  +:+ +:+       +:+        :+:+:+  +:+     +:+     +:+    +:+ +:+          
  +#+    +:+ +#+ +:+ +#+ +#++:++#  +#++:++#++ +#+ +:+ +#+     +#+     +#++:++#+  +#++:++#      
 +#+    +#+ +#+  +#+#+# +#+              +#+ +#+  +#+#+#     +#+     +#+        +#+            
#+#    #+# #+#   #+#+# #+#       #+#    #+# #+#   #+#+#     #+#     #+#        #+#             
########  ###    #### ########## ########  ###    #### ########### ###        ##########       \u001b[0m\n"""

DROPAPI = {
    "star.shopping": {
        "endpoint": "http://api.star.shopping/droptime/{}",
        "headers": {
            "Accept": "application/json",
            "User-Agent": "Sniper"
        },
        "key": "unix"
    },
    "coolkidmacho.com": {
        "endpoint": "https://api.coolkidmacho.com/droptime/{}",
        "headers": {
            "Accept": "application/json"
        },
        "key": "UNIX"
    }
}
