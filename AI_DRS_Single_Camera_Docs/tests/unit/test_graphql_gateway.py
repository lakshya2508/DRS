"""
Unit tests for Global Broadcast GraphQL Schema & API Gateway Module
"""

import pytest

from ai_drs.api.graphql_gateway import GraphQLGateway, GraphQLResponsePayload


def test_graphql_gateway_get_match():
    query = "{ getMatch(matchId: \"M_GQL_01\") { matchId runs wickets } }"
    res = GraphQLGateway.execute_query(query)

    assert isinstance(res, GraphQLResponsePayload)
    assert "getMatch" in res.data
    assert res.data["getMatch"]["matchId"] == "M_GQL_01"
    assert res.data["getMatch"]["runs"] == 178


def test_graphql_gateway_get_review():
    query = "{ getReview(reviewId: \"REV_101\") { decision confidence } }"
    res = GraphQLGateway.execute_query(query)

    assert "getReview" in res.data
    assert res.data["getReview"]["decision"] == "OUT"
