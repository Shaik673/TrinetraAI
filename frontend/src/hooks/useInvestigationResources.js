import { useQueries, useQuery } from '@tanstack/react-query'
import { api } from '../api/client'

const methods = {
  evidence: 'getInvestigationEvidence',
  assessments: 'getInvestigationAssessments',
  responses: 'getInvestigationResponses',
  verifications: 'getInvestigationVerifications',
  reflections: 'getInvestigationReflections',
  agents: 'getInvestigationAgents',
}

/** Load a resource from every investigation so the global operational screens
 * remain backed by the same data shown on the investigation detail screen. */
export function useInvestigationResources(resource) {
  const investigations = useQuery({
    queryKey: ['investigations'],
    queryFn: () => api.getInvestigations({ limit: 100 }).then((response) => response.data),
    refetchInterval: 15_000,
  })
  const method = methods[resource]
  const resourceQueries = useQueries({
    queries: (investigations.data || []).map((investigation) => ({
      queryKey: ['investigation', investigation.investigation_id, resource],
      queryFn: () => api[method](investigation.investigation_id).then((response) => response.data),
      refetchInterval: 15_000,
    })),
  })

  const items = resourceQueries.flatMap((query, index) =>
    (query.data || []).map((item) => ({ ...item, investigation: investigations.data[index] }))
  )

  return {
    items,
    investigations: investigations.data || [],
    isLoading: investigations.isLoading || resourceQueries.some((query) => query.isLoading),
    isError: investigations.isError || resourceQueries.some((query) => query.isError),
  }
}
