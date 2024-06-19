/*
 * Copyright 2023 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/* eslint-disable @typescript-eslint/no-explicit-any */

/**
 * Initializes a key in a map with provided defaultValue if it doesn't exist
 *
 * @param {!Object<!string, !any>} dataMap the parent map to update value
 * @param {!string} key the key to check in the map
 * @param {!any} defaultValue the default value to set
 * @return {!any} the value set for the key inside the parent map
 */
function initValueInMap({
  dataMap,
  key,
  defaultValue,
}: {
  dataMap: { [key: string]: string };
  key: string;
  defaultValue: any;
}) {
  dataMap[key] = dataMap[key] ?? defaultValue;
  return dataMap[key];
}

/**
 * Convert Array to HashMap
 *
 * Utility function to convert an Array to Hashmap
 * using the keyFn that computes the key from an
 * element or index of array
 *
 * Example: The following way will create a map
 * with id attribute as the key of the map
 * ```
 *   const arr = ...;
 *   arr.map(toHashMap((element)=> element.id));
 * ```
 *
 * @param {[]} arr
 * @param keyFn
 * @param valueFn
 * @returns {Map}
 */
function convertArrayToMap(arr: [], keyFn: any, valueFn = (x: any) => x) {
  if (typeof keyFn !== "function") {
    throw "KeyFn is undefined or not a function";
  }

  if (typeof valueFn !== "function") {
    throw "valueFn is undefined or not a function";
  }

  if (!arr || !Array.isArray(arr) || arr.length === 0) {
    return new Map();
  }

  return arr.reduce((map, element) => {
    (<any>map)[keyFn(element)] = valueFn(element);
    return map;
  }, new Map());
}

/**
 * Executes the provided function {fn} if its a type of function and passes it all the arguments
 * @param {?function} fn
 * @param {*} args
 * @return {*} the return type of function or `undefined`
 */
function checkAndExecuteFn(fn: (...args: any[]) => any, ...args: any[]): any {
  if (fn && typeof fn === "function") {
    return fn(...args);
  }
}

/**
 * Given a machine type return the accelerator count
 * @param machineType A100 or NVIDIA_L4 machine type
 */
function calculateAcceleratorCount(machineType: string): string {
  switch (machineType) {
    case "g2-standard-48":
      return "4";
    case "g2-standard-96":
      return "8";
    case "a2-highgpu-2g":
      return "2";
    case "a2-highgpu-4g":
      return "4";
    case "a2-highgpu-8g":
      return "8";
    case "a2-megagpu-16g":
      return "16";
    case "a2-ultragpu-1g":
      return "1";
    case "a2-ultragpu-2g":
      return "2";
    case "a2-ultragpu-4g":
      return "4";
    case "a2-ultragpu-8g":
      return "8";
    case "a3-highgpu-8g":
      return "8";
    default:
      return "1";
  }
}

class AttributeData {
  attribute: object;
  value: AttributeValue;
  valid: boolean;
  /**
   * @param {!Object} attribute
   * @param {AttributeValue} [value={}] the attribute's value
   * @param {boolean} [valid=true] the validity check result.
   */
  constructor(attribute: any, value = new AttributeValue(), valid = true) {
    this.attribute = attribute;
    this.value = value;
    this.valid = valid;
  }
}

class AttributeValue {
  simpleValue?: string | null;
  repeatedValues?: Array<AttributeValue> | null;
  nestedValues?: { [key: string]: AttributeData };
  /**
   *
   * @param {?string} simpleValue
   * @param {?Array<AttributeValue>} repeatedValues
   * @param {?Object<string, AttributeData>} nestedValues
   */
  constructor(
    simpleValue?: string | null,
    repeatedValues?: Array<AttributeValue> | null,
    nestedValues?: { [key: string]: AttributeData },
  ) {
    this.simpleValue = simpleValue;
    this.repeatedValues = repeatedValues;
    this.nestedValues = nestedValues;
  }
}

class ComponentData {
  component: object;
  attributeData?: { [key: string]: AttributeData };
  skipped: boolean;
  valid: boolean;
  /**
   *
   * @param {!Object} component
   * @param {Object<string,AttributeData>} attributeData
   * @param {Object} selectedAlternative
   * @param {boolean} [skipped=false]
   * @param {boolean} [valid
   */
  constructor(
    component: object,
    attributeData = {},
    skipped = false,
    valid = false,
  ) {
    this.component = component;
    this.attributeData = attributeData;
    this.skipped = skipped;
    this.valid = valid;
  }
}

class ComponentValidation {
  componentData: ComponentData;
  /**
   *
   * @param {!ComponentData} componentData
   */
  constructor(componentData: ComponentData) {
    this.componentData = componentData;
  }
}

export {
  initValueInMap,
  convertArrayToMap,
  checkAndExecuteFn,
  calculateAcceleratorCount,
  ComponentData,
  AttributeData,
  AttributeValue,
  ComponentValidation,
};
