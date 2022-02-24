import numpy as np

from great_expectations.data_context import DataContext
from great_expectations.execution_engine.execution_engine import MetricDomainTypes
from great_expectations.rule_based_profiler.parameter_builder import (
    NumericMetricRangeMultiBatchParameterBuilder,
)
from great_expectations.rule_based_profiler.types import (
    Domain,
    ParameterContainer,
    get_parameter_value_by_fully_qualified_parameter_name,
)


def test_bootstrap_numeric_metric_range_multi_batch_parameter_builder_bobby(
    bobby_columnar_table_multi_batch_deterministic_data_context,
):
    data_context: DataContext = (
        bobby_columnar_table_multi_batch_deterministic_data_context
    )

    # BatchRequest yielding two batches (January, 2019 and February, 2019 trip data)
    batch_request: dict = {
        "datasource_name": "taxi_pandas",
        "data_connector_name": "monthly",
        "data_asset_name": "my_reports",
    }

    numeric_metric_range_parameter_builder: NumericMetricRangeMultiBatchParameterBuilder = NumericMetricRangeMultiBatchParameterBuilder(
        name="row_count_range",
        metric_name="table.row_count",
        sampling_method="bootstrap",
        false_positive_rate=1.0e-2,
        round_decimals=0,
        data_context=data_context,
        batch_request=batch_request,
    )

    parameter_container: ParameterContainer = ParameterContainer(parameter_nodes=None)
    domain: Domain = Domain(
        domain_type=MetricDomainTypes.TABLE,
    )

    assert parameter_container.parameter_nodes is None

    numeric_metric_range_parameter_builder._build_parameters(
        parameter_container=parameter_container, domain=domain
    )

    assert len(parameter_container.parameter_nodes) == 1

    fully_qualified_parameter_name_for_value: str = "$parameter.row_count_range"
    expected_value: dict = {
        "value": {"value_range": None},
        "details": {
            "metric_configuration": {
                "domain_kwargs": {},
                "metric_name": "table.row_count",
            },
            "num_batches": 3,
        },
    }

    actual_value = get_parameter_value_by_fully_qualified_parameter_name(
        fully_qualified_parameter_name=fully_qualified_parameter_name_for_value,
        domain=domain,
        parameters={domain.id: parameter_container},
    )
    value = actual_value.pop("value")
    actual_value["value"] = {"value_range": None}

    assert actual_value == expected_value

    assert type(value["value_range"]) == np.ndarray