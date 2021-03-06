from constant_sorrow.constants import FLEET_STATES_MATCH
from nucypher.utilities.sandbox.ursula import make_federated_ursulas
from functools import partial


def test_all_nodes_have_same_fleet_state(federated_ursulas):
    checksums = [u.known_nodes.checksum for u in federated_ursulas]
    assert len(set(checksums)) == 1  # There is only 1 unique value.


def test_teacher_nodes_cycle(federated_ursulas):
    ursula = list(federated_ursulas)[0]

    # Before we start learning, Ursula has no teacher.
    assert ursula._current_teacher_node is None

    # Once we start, Ursula picks a teacher node.
    ursula.learn_from_teacher_node()
    first_teacher = ursula._current_teacher_node

    # When she learns the second time, it's from a different teacher.
    ursula.learn_from_teacher_node()
    second_teacher = ursula._current_teacher_node

    assert first_teacher != second_teacher


def test_nodes_with_equal_fleet_state_do_not_send_anew(federated_ursulas):
    some_ursula = list(federated_ursulas)[2]
    another_ursula = list(federated_ursulas)[3]

    # These two have the same fleet state.
    assert some_ursula.known_nodes.checksum == another_ursula.known_nodes.checksum
    some_ursula._current_teacher_node = another_ursula
    result = some_ursula.learn_from_teacher_node()
    assert result is FLEET_STATES_MATCH


def test_old_state_is_preserved(federated_ursulas, ursula_federated_test_config):
    lonely_ursula_maker = partial(make_federated_ursulas,
                                  ursula_config=ursula_federated_test_config,
                                  quantity=1,
                                  know_each_other=False)
    another_ursula = lonely_ursula_maker().pop()

    # This Ursula doesn't know about any nodes.
    assert len(another_ursula.known_nodes) == 0

    some_ursula_in_the_fleet = list(federated_ursulas)[0]
    another_ursula.remember_node(some_ursula_in_the_fleet)
    checksum_after_learning_one = another_ursula.known_nodes.checksum

    another_ursula_in_the_fleet = list(federated_ursulas)[1]
    another_ursula.remember_node(another_ursula_in_the_fleet)
    checksum_after_learning_two = another_ursula.known_nodes.checksum

    assert checksum_after_learning_one != checksum_after_learning_two

    assert another_ursula.known_nodes.states[checksum_after_learning_one].nodes == [some_ursula_in_the_fleet, another_ursula]
    assert another_ursula.known_nodes.states[checksum_after_learning_two].nodes == [some_ursula_in_the_fleet, another_ursula_in_the_fleet, another_ursula]
