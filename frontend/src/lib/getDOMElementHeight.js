export function getDOMElementHeight(el, {margins = false, borders = false}) {
  el = (typeof el === 'string') ? document.querySelector(el) : el

  let height = el.scrollHeight
  const styles = window.getComputedStyle(el)

  const margin = parseFloat(styles['marginTop']) +
      parseFloat(styles['marginBottom'])
  if (margins) height += margin

  const border = parseFloat(styles['borderTop']) +
      parseFloat(styles['borderBottom'])
  if (borders) height += border

  return height
}
