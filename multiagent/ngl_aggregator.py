class NGLAggregator:
    def __init__(self):
        self.weights = {
            "surgeon": 0.35,
            "physiotherapist": 0.35,
            "doctor": 0.30
        }
    
    def generate_agreed_viewpoints(self, responses):
        """
        Identify and generate viewpoints that all experts agree upon.
        
        Args:
            responses (dict): Dictionary containing responses from different experts
            
        Returns:
            list: List of agreed viewpoints
        """
        agreed_points = []
        all_viewpoints = {}
        
        # Extract key points from each response
        for expert, response in responses.items():
            points = [point.strip() for point in response.split('.') if point.strip()]
            all_viewpoints[expert] = points
        
        # Find common viewpoints across all experts
        if all_viewpoints:
            first_expert = list(all_viewpoints.keys())[0]
            potential_agreements = set(all_viewpoints[first_expert])
            
            for expert in all_viewpoints:
                if expert != first_expert:
                    potential_agreements &= set(all_viewpoints[expert])
            
            agreed_points = list(potential_agreements)
        
        return agreed_points

    def generate_conflicting_viewpoints(self, responses):
        """
        Identify and generate viewpoints where experts disagree.
        
        Args:
            responses (dict): Dictionary containing responses from different experts
            
        Returns:
            list: List of conflicting viewpoints with their sources
        """
        conflicts = []
        all_viewpoints = {}
        
        # Extract key points from each response
        for expert, response in responses.items():
            points = [point.strip() for point in response.split('.') if point.strip()]
            all_viewpoints[expert] = points
        
        # Compare viewpoints between experts
        experts = list(all_viewpoints.keys())
        for i in range(len(experts)):
            for j in range(i + 1, len(experts)):
                expert1, expert2 = experts[i], experts[j]
                for point1 in all_viewpoints[expert1]:
                    for point2 in all_viewpoints[expert2]:
                        if self._are_conflicting(point1, point2):
                            conflicts.append({
                                'point1': {'expert': expert1, 'view': point1},
                                'point2': {'expert': expert2, 'view': point2}
                            })
        
        return conflicts

    def _are_conflicting(self, point1, point2):
        """
        Helper method to determine if two viewpoints are conflicting.
        This is a simple implementation that could be enhanced with NLP.
        """
        # Simple contradiction detection based on negation
        negation_words = ['not', 'never', 'no', 'disagree']
        has_negation1 = any(word in point1.lower() for word in negation_words)
        has_negation2 = any(word in point2.lower() for word in negation_words)
        
        # If one point has negation and they're talking about the same topic
        similar_words = set(point1.lower().split()) & set(point2.lower().split())
        return (has_negation1 != has_negation2) and len(similar_words) > 2

    def resolve_conflicts(self, conflicts):
        """
        Attempt to resolve conflicts using weighted expert opinions.
        
        Args:
            conflicts (list): List of conflicting viewpoints
            
        Returns:
            list: Resolved viewpoints with explanations
        """
        resolved_conflicts = []
        
        for conflict in conflicts:
            expert1 = conflict['point1']['expert']
            expert2 = conflict['point2']['expert']
            
            # Use expert weights to determine resolution
            weight1 = self.weights[expert1]
            weight2 = self.weights[expert2]
            
            resolution = {
                'original_conflict': conflict,
                'resolution': conflict['point1']['view'] if weight1 > weight2 else conflict['point2']['view'],
                'explanation': f"Resolved in favor of {expert1 if weight1 > weight2 else expert2} based on expert weighting",
                'confidence': abs(weight1 - weight2) / max(weight1, weight2)
            }
            
            resolved_conflicts.append(resolution)
        
        return resolved_conflicts

    def generate_isolated_viewpoints(self, responses):
        """
        Identify viewpoints that are unique to individual experts.
        
        Args:
            responses (dict): Dictionary containing responses from different experts
            
        Returns:
            dict: Dictionary of isolated viewpoints by expert
        """
        isolated_points = {}
        all_viewpoints = {}
        
        # Extract key points from each response
        for expert, response in responses.items():
            points = [point.strip() for point in response.split('.') if point.strip()]
            all_viewpoints[expert] = points
            isolated_points[expert] = []
        
        # Find points unique to each expert
        for expert1, points1 in all_viewpoints.items():
            for point in points1:
                is_isolated = True
                for expert2, points2 in all_viewpoints.items():
                    if expert1 != expert2:
                        if any(self._are_similar(point, p2) for p2 in points2):
                            is_isolated = False
                            break
                if is_isolated:
                    isolated_points[expert1].append(point)
        
        return isolated_points

    def _are_similar(self, point1, point2):
        """
        Helper method to determine if two viewpoints are similar.
        This is a simple implementation that could be enhanced with NLP.
        """
        # Simple similarity check based on common words
        words1 = set(point1.lower().split())
        words2 = set(point2.lower().split())
        common_words = words1 & words2
        return len(common_words) > len(words1) * 0.5 or len(common_words) > len(words2) * 0.5

    def collect_viewpoints(self, agreed, conflicting, isolated):
        """
        Collect all viewpoints into a structured format.
        
        Args:
            agreed (list): Agreed viewpoints
            conflicting (list): Conflicting viewpoints
            isolated (dict): Isolated viewpoints
            
        Returns:
            dict: Structured collection of all viewpoints
        """
        return {
            "agreed_viewpoints": agreed,
            "conflicting_viewpoints": conflicting,
            "isolated_viewpoints": isolated
        }

    def generate_aggregated_response(self, viewpoints, resolved_conflicts):
        """
        Generate a final aggregated response incorporating all viewpoint types.
        
        Args:
            viewpoints (dict): Collected viewpoints
            resolved_conflicts (list): List of resolved conflicts
            
        Returns:
            dict: Final aggregated response with structured analysis
        """
        aggregated_response = {
            "consensus_points": viewpoints["agreed_viewpoints"],
            "resolved_conflicts": resolved_conflicts,
            "expert_specific_insights": viewpoints["isolated_viewpoints"],
            "summary": self._generate_summary(viewpoints, resolved_conflicts)
        }
        
        return aggregated_response

    def _generate_summary(self, viewpoints, resolved_conflicts):
        """
        Generate a concise summary of all viewpoints and resolutions.
        """
        summary_points = []
        
        # Add agreed points
        if viewpoints["agreed_viewpoints"]:
            summary_points.append("Consensus Points:")
            summary_points.extend([f"- {point}" for point in viewpoints["agreed_viewpoints"]])
        
        # Add resolved conflicts
        if resolved_conflicts:
            summary_points.append("\nResolved Disagreements:")
            for resolution in resolved_conflicts:
                summary_points.append(f"- {resolution['resolution']} ({resolution['explanation']})")
        
        # Add key isolated points
        if viewpoints["isolated_viewpoints"]:
            summary_points.append("\nUnique Expert Insights:")
            for expert, points in viewpoints["isolated_viewpoints"].items():
                if points:
                    summary_points.append(f"- {expert}: {points[0]}")
        
        return "\n".join(summary_points)

    def aggregate_responses(self, responses):
        """
        Main method to process and aggregate all responses using the new viewpoint analysis system.
        
        Args:
            responses (dict): Dictionary containing responses from different experts
            
        Returns:
            dict: Complete analysis and aggregated response
        """
        if not responses:
            return {"error": "No responses to aggregate"}

        # Generate different types of viewpoints
        agreed_viewpoints = self.generate_agreed_viewpoints(responses)
        conflicting_viewpoints = self.generate_conflicting_viewpoints(responses)
        resolved_conflicts = self.resolve_conflicts(conflicting_viewpoints)
        isolated_viewpoints = self.generate_isolated_viewpoints(responses)
        
        # Collect all viewpoints
        all_viewpoints = self.collect_viewpoints(
            agreed_viewpoints,
            conflicting_viewpoints,
            isolated_viewpoints
        )
        
        # Generate final aggregated response
        final_response = self.generate_aggregated_response(all_viewpoints, resolved_conflicts)
        
        # Include original responses and confidence scores
        final_response.update({
            "individual_responses": responses,
            "confidence_scores": {
                expert: min(len(response.split()) / 100, 1.0)
                for expert, response in responses.items()
            }
        })
        
        return final_response

    def analyze_agreement(self, responses):
        """
        Analyze points of agreement and disagreement between experts.
        This is a placeholder for more sophisticated analysis.
        """
        # This would be enhanced with NLP techniques to identify
        # common themes, contradictions, and key points
        pass 