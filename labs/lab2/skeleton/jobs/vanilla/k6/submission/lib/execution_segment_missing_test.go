package lib

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// Test 1: Creating execution segment sequences from string inputs and working
// with the resulting segments.
func TestNewExecutionSegmentSequenceFromString(t *testing.T) {
	t.Parallel()

	t.Run("valid sequence", func(t *testing.T) {
		t.Parallel()
		ess, err := NewExecutionSegmentSequenceFromString("0,1/3,2/3,1")
		require.NoError(t, err)
		require.Len(t, ess, 3)
		assert.Equal(t, "0:1/3", ess[0].String())
		assert.Equal(t, "1/3:2/3", ess[1].String())
		assert.Equal(t, "2/3:1", ess[2].String())
		// the segments chain together without gaps or overlaps
		assert.Equal(t, ess[0].to, ess[1].from)
		assert.Equal(t, ess[1].to, ess[2].from)
		assert.True(t, ess.IsFull())
	})

	t.Run("mixed formats", func(t *testing.T) {
		t.Parallel()
		ess, err := NewExecutionSegmentSequenceFromString("0,50%,0.75,1")
		require.NoError(t, err)
		require.Len(t, ess, 3)
		assert.Equal(t, "0:1/2", ess[0].String())
		assert.Equal(t, "1/2:3/4", ess[1].String())
		assert.Equal(t, "3/4:1", ess[2].String())
	})

	t.Run("empty string is nil sequence", func(t *testing.T) {
		t.Parallel()
		ess, err := NewExecutionSegmentSequenceFromString("")
		require.NoError(t, err)
		assert.Nil(t, ess)
	})

	t.Run("single point is an error", func(t *testing.T) {
		t.Parallel()
		_, err := NewExecutionSegmentSequenceFromString("0")
		assert.Error(t, err)
	})

	t.Run("non-contiguous points are an error", func(t *testing.T) {
		t.Parallel()
		_, err := NewExecutionSegmentSequenceFromString("0,1/2,1/4,1")
		assert.Error(t, err)
	})

	t.Run("invalid point is an error", func(t *testing.T) {
		t.Parallel()
		_, err := NewExecutionSegmentSequenceFromString("0,abc,1")
		assert.Error(t, err)
	})
}

// Test 2: Working with execution segments to compute striped offsets in
// different usage situations.
func TestExecutionTupleGetStripedOffsets(t *testing.T) {
	t.Parallel()

	t.Run("two equal halves", func(t *testing.T) {
		t.Parallel()
		ess, err := NewExecutionSegmentSequenceFromString("0,1/2,1")
		require.NoError(t, err)
		et, err := NewExecutionTuple(ess[0], &ess)
		require.NoError(t, err)
		start, offsets, lcd := et.GetStripedOffsets()
		assert.Equal(t, int64(0), start)
		assert.Equal(t, []int64{2}, offsets)
		assert.Equal(t, int64(2), lcd)

		et, err = NewExecutionTuple(ess[1], &ess)
		require.NoError(t, err)
		start, offsets, lcd = et.GetStripedOffsets()
		assert.Equal(t, int64(1), start)
		assert.Equal(t, []int64{2}, offsets)
		assert.Equal(t, int64(2), lcd)
	})

	t.Run("three equal thirds", func(t *testing.T) {
		t.Parallel()
		ess, err := NewExecutionSegmentSequenceFromString("0,1/3,2/3,1")
		require.NoError(t, err)
		for i, expectedStart := range []int64{0, 1, 2} {
			et, err := NewExecutionTuple(ess[i], &ess)
			require.NoError(t, err)
			start, offsets, lcd := et.GetStripedOffsets()
			assert.Equal(t, expectedStart, start)
			assert.Equal(t, []int64{3}, offsets)
			assert.Equal(t, int64(3), lcd)
		}
	})

	t.Run("unequal 3/5 and 2/5 segments", func(t *testing.T) {
		t.Parallel()
		ess, err := NewExecutionSegmentSequenceFromString("0,3/5,1")
		require.NoError(t, err)
		et, err := NewExecutionTuple(ess[0], &ess)
		require.NoError(t, err)
		start, offsets, lcd := et.GetStripedOffsets()
		assert.Equal(t, int64(0), start)
		assert.Equal(t, []int64{2, 2, 1}, offsets)
		assert.Equal(t, int64(5), lcd)

		et, err = NewExecutionTuple(ess[1], &ess)
		require.NoError(t, err)
		start, offsets, lcd = et.GetStripedOffsets()
		assert.Equal(t, int64(1), start)
		assert.Equal(t, []int64{2, 3}, offsets)
		assert.Equal(t, int64(5), lcd)
	})

	t.Run("single full segment", func(t *testing.T) {
		t.Parallel()
		et, err := NewExecutionTuple(nil, nil)
		require.NoError(t, err)
		start, offsets, lcd := et.GetStripedOffsets()
		assert.Equal(t, int64(0), start)
		assert.Equal(t, []int64{1}, offsets)
		assert.Equal(t, int64(1), lcd)
	})
}

// Test 3: Working with execution segment sequences to derive shared numeric
// properties (the least common denominator) from their values.
func TestExecutionSegmentSequenceLCD(t *testing.T) {
	t.Parallel()

	testCases := []struct {
		name   string
		seq    string
		expect int64
	}{
		{name: "halves", seq: "0,1/2,1", expect: 2},
		{name: "thirds", seq: "0,1/3,2/3,1", expect: 3},
		{name: "quarters", seq: "0,1/4,1/2,3/4,1", expect: 4},
		{name: "fifths", seq: "0,3/5,1", expect: 5},
		{name: "mixed denominators", seq: "0,1/2,3/4,1", expect: 4},
		{name: "full", seq: "0,1", expect: 1},
	}

	for _, testCase := range testCases {
		testCase := testCase
		t.Run(testCase.name, func(t *testing.T) {
			t.Parallel()
			ess, err := NewExecutionSegmentSequenceFromString(testCase.seq)
			require.NoError(t, err)
			assert.Equal(t, testCase.expect, ess.LCD())
		})
	}
}

// Test 4: Creating a new execution tuple based on a numeric input applied to
// an existing execution segment setup.
func TestExecutionTupleGetNewExecutionTupleFromValue(t *testing.T) {
	t.Parallel()

	t.Run("re-segment thirds with value 2", func(t *testing.T) {
		t.Parallel()
		ess, err := NewExecutionSegmentSequenceFromString("0,1/3,2/3,1")
		require.NoError(t, err)
		et, err := NewExecutionTuple(ess[0], &ess)
		require.NoError(t, err)

		newET, err := et.GetNewExecutionTupleFromValue(2)
		require.NoError(t, err)
		// the first third (0:1/3) gets 1 of the 2 elements, so the new
		// segment is (0, 1/2]
		assert.Equal(t, "0:1/2", newET.Segment.String())
		assert.Equal(t, 0, newET.SegmentIndex)
		assert.Equal(t, int64(25), newET.ScaleInt64(50))
		assert.Equal(t, int64(1), newET.ScaleInt64(1))
		assert.Equal(t, int64(0), newET.ScaleInt64(0))
	})

	t.Run("value divisible by the LCD keeps the same tuple", func(t *testing.T) {
		t.Parallel()
		ess, err := NewExecutionSegmentSequenceFromString("0,1/3,2/3,1")
		require.NoError(t, err)
		et, err := NewExecutionTuple(ess[1], &ess)
		require.NoError(t, err)

		newET, err := et.GetNewExecutionTupleFromValue(3)
		require.NoError(t, err)
		assert.Equal(t, "1/3:2/3", newET.Segment.String())
		assert.Equal(t, 1, newET.SegmentIndex)
		assert.Equal(t, int64(17), newET.ScaleInt64(50))
	})

	t.Run("segment dropped from the new sequence is an error", func(t *testing.T) {
		t.Parallel()
		ess, err := NewExecutionSegmentSequenceFromString("0,1/3,2/3,1")
		require.NoError(t, err)
		et, err := NewExecutionTuple(ess[1], &ess)
		require.NoError(t, err)

		// with a value of 1, the middle third gets no elements, so it is
		// dropped from the new sequence
		_, err = et.GetNewExecutionTupleFromValue(1)
		assert.Error(t, err)
	})

	t.Run("value below 1 is an error", func(t *testing.T) {
		t.Parallel()
		ess, err := NewExecutionSegmentSequenceFromString("0,1/3,2/3,1")
		require.NoError(t, err)
		et, err := NewExecutionTuple(ess[0], &ess)
		require.NoError(t, err)

		_, err = et.GetNewExecutionTupleFromValue(0)
		assert.Error(t, err)
	})
}
