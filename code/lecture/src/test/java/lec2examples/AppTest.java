package lec2examples;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.stream.Stream;

/**
 * Unit test for simple App.
 */
class AppTest {
    /**
     * Rigorous Test.
     */

    @ParameterizedTest
    @MethodSource("numZeroTestCases")
    void testNumZero(int[] input, int expected) {
        assertEquals(App.numZero(input), expected);
    }

    static Stream<Arguments> numZeroTestCases() {
        return Stream.of(
            Arguments.of(new int[]{1, 2, 3}, 0),
            Arguments.of(new int[]{0, 45, 0}, 2),
            Arguments.of(new int[]{-1, 1}, 0),
            Arguments.of(new int[]{}, 0)
        );
    }
}
