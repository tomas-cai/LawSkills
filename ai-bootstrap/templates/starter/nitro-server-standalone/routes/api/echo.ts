// 最小示例：后续按产品域拆分 auth / jobs / resumes / matches / exports
export default defineEventHandler((event) => {
  const query = getQuery(event)
  const name = typeof query.name === 'string' && query.name.trim() ? query.name.trim() : 'world'
  return { message: `hello ${name}` }
})
