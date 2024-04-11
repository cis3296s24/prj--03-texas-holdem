import numpy as np
import card


class Ranker:
    @staticmethod
    def rank_all_hands(hand_combos, return_all=False):
        results = []

        for hand in hand_combos:
            rank, tie_breakers = Ranker.rank_one_hand(hand)
            results.append((rank, tie_breakers))

        if return_all:
            return results
        else:
            # Sort the results based on rank and then tie_breakers, return the highest
            highest_hand = max(results, key=lambda x: (x[0], x[1]))
            return highest_hand


    @staticmethod
    def rank_one_hand(hand):
        counts = np.array([card.count for card in hand])
        colors = np.array([card.color for card in hand])

        # Sort the counts to make further operations easier.
        counts.sort()
        suit_arr = Ranker.gen_suit_arr(colors)
        straight_arr = Ranker.gen_straight_arr(counts)

        rank = 0
        tie_breakers = []

        # The checks return a tuple (rank, tie_breakers), we update both based on the check.
        rank, tie_breakers = Ranker.straight_flush_check(counts, rank, straight_arr, suit_arr)
        if rank == 0:  # Continue only if no higher rank was found
            rank, tie_breakers = Ranker.four_of_a_kind_check(counts, rank)
        if rank == 0:
            rank, tie_breakers = Ranker.full_house_check(counts, rank)
        if rank == 0:
            rank, tie_breakers = Ranker.flush_check(rank, suit_arr, counts)
        if rank == 0:
            rank, tie_breakers = Ranker.straight_check(counts, rank, straight_arr)
        if rank == 0:
            rank, tie_breakers = Ranker.three_of_a_kind_check(counts, rank)
        if rank == 0:
            rank, tie_breakers = Ranker.two_pairs_check(counts, rank)
        if rank == 0:
            rank, tie_breakers = Ranker.one_pair_check(counts, rank)
        if rank == 0:
            # High card case, return the sorted counts as tie_breakers.
            tie_breakers = sorted(counts, reverse=True)
            rank = 0  # Explicit for clarity, high card is the default case.

        return rank, tie_breakers


    @staticmethod
    def gen_suit_arr(colors):
        return np.max(colors) == np.min(colors)

    @staticmethod
    def gen_straight_arr(counts):
        straight_check = 0
        for i in range(4):
            if counts[i] + 1 == counts[i + 1]:
                straight_check += 1
        straight_check += ((counts[0] == 2) and (counts[4] == 14))  # Handling Ace as both high and low
        return straight_check == 4

    @staticmethod
    def straight_flush_check(counts, rank, straight_arr, suit_arr):
        if rank == 0 and straight_arr and suit_arr:
            # Handling Ace as both high and low in a straight flush
            if counts[0] == 2 and counts[4] == 14:
                # Ace-low straight flush, make Ace '1'
                return (8, [5])  # Returning 5 as the highest card (Ace is considered low)
            return (8, [counts[-1]])  # Return rank and highest card of straight flush
        return (rank, [])


    @staticmethod
    def four_of_a_kind_check(counts, rank):
        if rank > 0:
            return (rank, [])
        quad_value = np.where(np.bincount(counts)[1:] == 4)[0]
        if quad_value.size > 0:
            quad_value += 1  # Adjusting index to match card value
            kicker = np.max(np.setdiff1d(counts, quad_value))
            return (7, [quad_value[0], kicker])  # Returning rank, quad value, and kicker
        return (rank, [])

    @staticmethod
    def full_house_check(counts, rank):
        if rank > 0:
            return (rank, [])
        count_bin = np.bincount(counts)[1:]
        if 3 in count_bin and 2 in count_bin:
            triplet_value = np.where(count_bin == 3)[0][0] + 1
            pair_value = np.where(count_bin == 2)[0][0] + 1
            return (6, [triplet_value, pair_value])
        return (rank, [])


    @staticmethod
    def flush_check(rank, suit_arr, counts):
        if rank > 0:
            return (rank, [])
        if suit_arr:
            # Return all cards in descending order
            return (5, sorted(counts, reverse=True))
        return (rank, [])


    @staticmethod
    def straight_check(counts, rank, straight_arr):
        if rank > 0:
            return (rank, [])
        if straight_arr:
            if counts[0] == 2 and counts[4] == 14:  # Ace low straight
                return (4, [5])  # Returning 5 as the highest card
            return (4, [counts[-1]])
        return (rank, [])


    @staticmethod
    def three_of_a_kind_check(counts, rank):
        if rank > 0:
            return (rank, [])
        triplet_value = np.where(np.bincount(counts)[1:] == 3)[0]
        if triplet_value.size > 0:
            triplet_value += 1  # Adjust for card value
            kickers = np.sort(np.setdiff1d(counts, triplet_value))[::-1]  # Highest kickers
            return (3, [triplet_value[0]] + list(kickers[:2]))  # Include top 2 kickers
        return (rank, [])

    @staticmethod
    def two_pairs_check(counts, rank):
        if rank > 0:
            return (rank, [])
        pair_values = np.where(np.bincount(counts)[1:] == 2)[0]
        if pair_values.size == 2:
            pair_values += 1  # Adjust for card values
            kicker = np.max(np.setdiff1d(counts, pair_values))  # Highest kicker
            return (2, sorted(pair_values, reverse=True) + [kicker])
        return (rank, [])


    @staticmethod
    def one_pair_check(counts, rank):
        if rank > 0:
            return (rank, [])
        pair_value = np.where(np.bincount(counts)[1:] == 2)[0]
        if pair_value.size > 0:
            pair_value += 1  # Adjust for card value
            kickers = np.sort(np.setdiff1d(counts, pair_value))[::-1]  # Highest kickers
            return (1, [pair_value[0]] + list(kickers[:3]))  # Include top 3 kickers
        return (rank, [])
