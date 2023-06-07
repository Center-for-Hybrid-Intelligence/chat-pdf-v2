export const isString = (v) => { return typeof v === 'string' || v instanceof String }
export const isNumber = (v) => { return typeof v === 'number' || v instanceof Number }
export const isNumeric = (v) => { return isNumber(v) || !isNaN(v) }
export const isBoolean = (v) => { return typeof v === 'boolean' || v instanceof Boolean }
export const isArray = (v) => { return Array.isArray(v) }
export const isRegExp = (v) => { return v instanceof RegExp }
export const isFunction = (v) => { return typeof v === 'function' || v instanceof Function }
export const isObject = (v, notStrict) => {
  return v !== null &&
      typeof v === 'object' &&
      (
          notStrict ||
          !notStrict &&
          v.constructor.toString().includes("Object")
      )
}
export const isIterable = (v) => isObject(v) || isArray(v)
export default function getVariableType(v) {
  let type = isString(v) ? 'String' : undefined
  if (!type) type = isNumber(v) ? 'Number' : undefined
  if (!type) type = isBoolean(v) ? 'Boolean' : undefined
  if (!type) type = isFunction(v) ? 'Function' : undefined
  if (!type) type = isRegExp(v) ? 'RegExp' : undefined
  if (!type) type = isArray(v) ? 'Array' : undefined
  if (!type) type = isObject(v) ? 'Object' : undefined
  return type
}
export const isPositiveNumber = v => isNumber(v) && v > 0

export const isArrayOfStrings = v => {
  let pass = isArray(v)
  if (pass) {
    v.forEach(item => pass = pass && isString(item))
  }
  return pass
}
