/* Copyright 2020 iExec Blockchain Tech
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*     http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/

pragma solidity >0.5.0 <0.7.0;

library LibSet_bytes32
{
	struct set
	{
		bytes32[] values;
		mapping(bytes32 => uint256) indexes;
	}

	function length(set storage _set)
	internal view returns (uint256)
	{
		return _set.values.length;
	}

	function at(set storage _set, uint256 _index)
	internal view returns (bytes32 )
	{
		return _set.values[_index - 1];
	}

	function indexOf(set storage _set, bytes32  _value)
	internal view returns (uint256)
	{
		return _set.indexes[_value];
	}

	function contains(set storage _set, bytes32  _value)
	internal view returns (bool)
	{
		return indexOf(_set, _value) != 0;
	}

	function content(set storage _set)
	internal view returns (bytes32[] memory)
	{
		return _set.values;
	}

	function add(set storage _set, bytes32  _value)
	internal returns (bool)
	{
		if (contains(_set, _value))
		{
			return false;
		}
		_set.values.push(_value);
		_set.indexes[_value] = _set.values.length;
		return true;
	}

	function remove(set storage _set, bytes32  _value)
	internal returns (bool)
	{
		if (!contains(_set, _value))
		{
			return false;
		}

		uint256 i    = indexOf(_set, _value);
		uint256 last = length(_set);

		if (i != last)
		{
			bytes32  swapValue = _set.values[last - 1];
			_set.values[i - 1] = swapValue;
			_set.indexes[swapValue] = i;
		}

		delete _set.indexes[_value];
		_set.values.pop();

		return true;
	}

	function clear(set storage _set)
	internal returns (bool)
	{
		for (uint256 i = _set.values.length; i > 0; --i)
		{
			delete _set.indexes[_set.values[i-1]];
		}
		_set.values = new bytes32[](0);
		return true;
	}
}
