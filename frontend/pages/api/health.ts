import type { NextApiRequest, NextApiResponse } from 'next'

export default function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  res.status(200).json({
    status: 'healthy',
    service: 'Grammy Engine Frontend',
    timestamp: new Date().toISOString()
  })
}
