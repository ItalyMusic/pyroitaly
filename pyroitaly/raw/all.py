#  PyroItaly - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#  Copyright (C) 2022-present Mayuri-Chan <https://github.com/Mayuri-Chan>
#  Copyright (C) 2025-present ItalyMusic <https://github.com/ItalyMusic>
#
#  This file is part of PyroItaly.
#
#  PyroItaly is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  PyroItaly is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with PyroItaly.  If not, see <http://www.gnu.org/licenses/>.

objects = {
    0xbc799737: "pyroitaly.raw.core.BoolFalse",
    0x997275b5: "pyroitaly.raw.core.BoolTrue",
    0x1cb5c415: "pyroitaly.raw.core.Vector",
    0x73f1f8dc: "pyroitaly.raw.core.MsgContainer",
    0xae500895: "pyroitaly.raw.core.FutureSalts",
    0x0949d9dc: "pyroitaly.raw.core.FutureSalt",
    0x3072cfa1: "pyroitaly.raw.core.GzipPacked",
    0x5bb8e511: "pyroitaly.raw.core.Message",
    
    # Add more objects as needed for your specific implementation
    # This is a minimal set to get the basic functionality working
    
    # Types
    0x2134579: "pyroitaly.raw.types.Null",
    0x3fedd339: "pyroitaly.raw.types.True",
    0xbc799737: "pyroitaly.raw.types.BoolFalse",
    0x997275b5: "pyroitaly.raw.types.BoolTrue",
    
    # Functions
    0x7abe77ec: "pyroitaly.raw.functions.Ping",
    0x78d4b1fb: "pyroitaly.raw.functions.GetConfig",
    
    # You would typically have hundreds of objects here
    # This is just a minimal set to get things working
}
