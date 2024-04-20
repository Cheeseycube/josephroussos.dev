!October 18, 2023. I'm tired of my program not working correctly when there
! are double or triple letters in a word, because I now have an easy solution.
! Because I know how to reproduce the wordle program output for a word, I can
! use that functionality to find out which words in the wordle dictionary are
! still possible after I get the wordle feedback.
!
! After I get the wordle feedback for my proposed word, I simply apply my
! proposed word to every word in the wordle dictionary. Every word that results
! in the same feedback gets POSSIBLE=1. Practically, I just give every word
! POSSIBLE=1 right off the bat, and then change it to POSSIBLE=0 if
! (1) the word has already been used in the past, or
! (2) the feedback for the word does not match the actual wordle feedback.
!
!October 10, 2023. Started working on new option for the evaluation phase
! allows the user to find the 10 best words in the dictionary according to
! four criteria: (1) minimax, (2) mean group size, (3) number of 1's, and
! (4) number of 1's and 2's.
!
!October 3, 2023. Modified the program so that it when it gives the grouping
! results, it also gives the grouping distribution.
!
!September 16, 2023. Modified the program so that when it does the evaluation
! of a proposed word against the remaining possible words, it groups together
! results that are alike.
!
!!March 27, 2023.  Expand the "all" list to over 12,000 words, so I had to
! change the dimension statements to handle that.  Also, the list is now
! in all lowercase letters, so I had to do the "cap check" on the entire list.
!
!October 27, 2022. Modified the program to provide the user with an option
! to evaluate the list of possible words by showing what the wordle output
! would be if you give the program a word and it treats each word in the list
! as the correct word. That way you can see if a given word can differentiate among
! all the possible words as a throw-away word.  I might restrict this option to
! only "short" lists, but I'm not sure how short "short" should be.  Logic would
! say that the list should be no longer than 32 because 2^5 is 32.  Practically,
! I would guess that 20 might be a good cut-off. But, then again, there are often
! words in the list that I think are not likely.  That is why a separate program
! to do this is also something that I might do.  So, I think I'll restrict it to
! 20, but also have a separate program where a person can input words.
!
!October 24, 2022. Modified the program to print out the letter distribution
! among the remaining words.  Prints out how many words have an A,
! how many have a B, how many have a C, etc.
!
!October 22, 2022. Modified the program to provide the user the option of
! updating "wordle_list_used.txt" by supplying the winning word.
!
!October 8, 2022.  Program to help me save time looking up words for Wordle.
! I tell the program what feedback I've had from Wordle, and it tells me what
! possible words are left.  That's all.
!*********************************************************************************

PROGRAM wordle_help
IMPLICIT NONE

INTEGER position_check_1(5000), position_check_2(5000), istar(5000), kount(200)
INTEGER grp_count(20000), real_kount(20000)
INTEGER kount_possible, grp_number, max_size, sum_grp_size, count_all, counter_all
REAL*16 xkount_possible, xgrp_number, mean_size, xsum_grp_size, mean_grp_size
CHARACTER*96 DIST_LABEL1
CHARACTER*15 DIST_LABEL2, DIST_LABEL3
INTEGER ones, ones_twos
INTEGER max_t10(20), ones_t10(20), ones_twos_t10(20)
INTEGER mean_t10_max(20), ones_t10_max(20), ones_twos_t10_max(20)
INTEGER mean_t10_ones(20), max_t10_ones(20), ones_twos_t10_ones(20)
REAL*16 max_t10_mean(20), ones_t10_mean(20), ones_twos_t10_mean(20)
INTEGER mean_t10_ones_twos(20), max_t10_ones_twos(20), ones_t10_ones_twos(20)
REAL*16 mean_t10(20)

INTEGER kount_words_with_A, kount_words_with_B, kount_words_with_C, kount_words_with_D
INTEGER kount_words_with_E, kount_words_with_F, kount_words_with_G, kount_words_with_H
INTEGER kount_words_with_I, kount_words_with_J, kount_words_with_K, kount_words_with_L
INTEGER kount_words_with_M
INTEGER kount_words_with_N, kount_words_with_O, kount_words_with_P, kount_words_with_Q
INTEGER kount_words_with_R, kount_words_with_S, kount_words_with_T, kount_words_with_U
INTEGER kount_words_with_V, kount_words_with_W, kount_words_with_X, kount_words_with_Y
INTEGER kount_words_with_Z
INTEGER chk_A,chk_B,chk_C,chk_D,chk_E,chk_F,chk_G,chk_H,chk_I,chk_J,chk_K,chk_L,chk_M
INTEGER chk_N,chk_O,chk_P,chk_Q,chk_R,chk_S,chk_T,chk_U,chk_V,chk_W,chk_X,chk_Y,chk_Z

INTEGER i, j, k, k2, l, count_wordle, count_wordle_used, try_count, idoc, idec, ichk
INTEGER idec_step2, idec_step3
INTEGER count_NOT_HERE(5), count_NOT_ANYWHERE

INTEGER MBS_chk(100), count_MBS
CHARACTER*1 cjunk, MBS(10), NOT_HERE(5,100), NOT_ANYWHERE(100)

CHARACTER*1 W(15000,5), proposed_word(10,5), pretend_prop_word(5), output(15000,5), ALL(15000,5)
CHARACTER*1 output_actual(10,5)
! W(15000,5) are the 2309 Wordle words, one character for each of the five letters.
! W(j,i)= the value of the letter in the i^th position in the j^th word.
! ALL(*,*) are all of the 12,917 5-letter words in the dictionary.
! proposed_word(j,i) is the value of the letter in the i^th position for the word proposed on Try j.
! output_actual(j,i) is the wordle feedback for the i^th position for the worde proposed on Try j.
! pretend_prop_word(5) is used for evaluating pretend proposed words
! output(15000,5) is the variable that stores the results for comparing a proposed word to the
!  remaining possible wordle words (up to 15,000 of them) to see what the wordle output would be
!  like if each possible word were the correct wordle word.

CHARACTER*1 prop_word_max_t10(20,5), prop_word_mean_t10(20,5)
CHARACTER*1 prop_word_ones_t10(20,5), prop_word_ones_twos_t10(20,5)

CHARACTER*1 USED(15000,5)
! USED(15000,5) are the Wordle words that have been used so far in the game.

CHARACTER*1 winning_word(5)
! winning_word(5) is the winning Wordle word for the day.

CHARACTER*10 Crit1,Crit2,Crit3,Crit4
CHARACTER*60 OUT_LABELS1,OUT_LABELS2,OUT_LABELS3,OUT_LABELS4

INTEGER IS_MUST(5)
CHARACTER*1 ML(5)
! IS_MUST(i)=1, means that a Must exists for Position i.
! IS_MUST(i)=0, means that a Must does not exist for Letter i.
! When IS_MUST(i)=1, then ML(i)= the value the letter must have for position i.
! When IS_MUST(i)=0, then ML(i)=' '.  a blank character.

INTEGER POSSIBLE(15000)
! POSSIBLE(i)=1 if the i^th Wordle word is possible; o.w., it is zero.

!Read in all the wordle words
OPEN(unit=1,file='wordle_list_all.txt')

i=0
do
	i=i+1
	read(1,11,end=9) (W(i,j), j=1,5)
        POSSIBLE(i)=1
	do j=1,5
		call cap_check(w(i,j))
	enddo
! at first, all wordle words are possible to be the answer
11	format(5a1)

enddo
9 continue
count_wordle = i-1
write(*,*) 'number of wordle words read in = ',count_wordle

CLOSE(1)


!Read in all the used wordle words
OPEN(unit=1,file='wordle_list_used.txt')

i=1
do
	read(1,11,end=99) (USED(i,j), j=1,5)
	i=i+1

enddo
99 continue
count_wordle_used = i-1
write(*,*) 'number of used wordle words read in = ',count_wordle_used

CLOSE(1)

!Read in all the dictionary of 5-letter words
OPEN(unit=1,file='word_list_all.txt')

i=1
do
	read(1,11,end=999) (ALL(i,j), j=1,5)
	do j=1,5
		call cap_check(all(i,j))
	enddo
	i=i+1
enddo

999 continue
count_all = i-1

write(*,*) 'number of all possible 5-letter words read in = ',count_all

!At this point, may as well reduce the POSSIBLE words
!by taking away the words that have already been used.
!skip this step if the number of used words is zero.

if(count_wordle_used.eq.0) goto 325

do i=1,count_wordle

	if(POSSIBLE(i).eq.1) then
		do k=1,count_wordle_used
			do j=1,5
				if(W(i,j).eq.USED(k,j)) then
					!go to the next letter
					go to 55
				else
					!go to the next used word
					go to 65
				endif
			55 continue
			!if we make it this far with j=5, then the word has already been used
			if(j.eq.5) then
				POSSIBLE(i)=0
				!go to the next value of i
				go to 75
			endif
			enddo
		65 continue
		enddo
	endif
75 continue
enddo

325 continue


!I think the next thing to do is to simply have the user input the feedback
!from the wordle program, and doing this over and over until the user wants
!to stop.  technically, you can go more than 6 tries.

try_count=0

15 continue

try_count = try_count + 1

write(*,*) ' '
write(*,*) ' Will now have you enter the feedback for Try number ', try_count

do l=1,5

write(*,*) ' For Letter Position ',l,':'
write(*,*) '     Enter  1, if the wordle feedback was a MUST for this letter in this particular position'
write(*,*) '     Enter  0, if the wordle feedback was a MUST for this letter but NOT in this particular position'
write(*,*) '     Enter -1, if the wordle feedback was a NOT anywhere in the word for this letter (or not in this'
write(*,*) '               position if it appears in some other position'
	read(*,*) idoc

	if(idoc.eq.1) then
  		write(*,*) ' Enter the MUST letter for Position ',l, ':'
  		read(*,*)  proposed_word(try_count,l)
		call cap_check(proposed_word(try_count,l))
		output_actual(try_count,l)=proposed_word(try_count,l)
	elseif(idoc.eq.0) then
		write(*,*) ' Enter the MUST-BE-SOMEWHERE-BUT-NOT-HERE Letter:'
                read(*,*) proposed_word(try_count,l)
		call lower_case_check(proposed_word(try_count,l))
		output_actual(try_count,l)=proposed_word(try_count,l)
	else
  		write(*,*) ' Enter the NOT-ANYWHERE letter for the wordle word:'
  		read(*,*) proposed_word(try_count,l)
		output_actual(try_count,l)='*'
	endif

enddo
!At this point we can figure out all the remaining possible words by applying the proposed word to every
!POSSIBLE(i)=1 word in the wordle dictionary and see which words have the same output as the actual wordle output.
!Any word that does not have the same output will be marked as POSSIBLE(i)=0.

do i=1,count_wordle
	if(POSSIBLE(i).eq.1) then
!this is the tough part. figuring out the wordle output
		do k=1,5
			position_check_1(k)=0
			position_check_2(k)=0
			output(i,k) = '*'
		enddo

		do j=1,5
			call cap_check(proposed_word(try_count,j))
		enddo

!first check to see if any letters are correct and in the right place

		do j=1,5
			if(proposed_word(try_count,j).eq.W(i,j)) then
!right letter and in the right place
				call cap_check(proposed_word(try_count,j))
				output(i,j) = proposed_word(try_count,j)
!keep track of which positions in W(i,j) have been matched to a position in proposed_word()
				position_check_1(j) = 1
			endif
		enddo

		do k=1,5
			if(position_check_1(k).eq.1) go to 135
			do j=1,5
!if jth position in W(i,j) already perfectly matches the same position in proposed_word(), skip this value of j
				if(position_check_1(j).eq.1) go to 145
!if jth position in W(i,j) has already been matched in Loop 2, skip this value of j
				if(position_check_2(j).eq.1) go to 145
				if(proposed_word(try_count,k).eq.W(i,j)) then
!right letter wrong place
					call lower_case_check(proposed_word(try_count,k))
					output(i,k) = proposed_word(try_count,k)
					position_check_2(j) = 1
					go to 135
				endif
				145 continue
			enddo
			135 continue
		enddo
!At this point, we have produced the output for a word with POSSIBLE=1
!If this output does not match output_actual, then we need to change POSSIBLE=1 to POSSIBLE=0
		do j=1,5
			if(output(i,j).ne.output_actual(try_count,j)) then
				POSSIBLE(i)=0
				goto 335
			endif
		enddo
335		continue
	endif
enddo


!Now we can print out all the wordle words with POSSIBLE(i)=1
!and count the number of possible words.

kount_possible = 0

kount_words_with_A = 0
kount_words_with_B = 0
kount_words_with_C = 0
kount_words_with_D = 0
kount_words_with_E = 0
kount_words_with_F = 0
kount_words_with_G = 0
kount_words_with_H = 0
kount_words_with_I = 0
kount_words_with_J = 0
kount_words_with_K = 0
kount_words_with_L = 0
kount_words_with_M = 0
kount_words_with_N = 0
kount_words_with_O = 0
kount_words_with_P = 0
kount_words_with_Q = 0
kount_words_with_R = 0
kount_words_with_S = 0
kount_words_with_T = 0
kount_words_with_U = 0
kount_words_with_V = 0
kount_words_with_W = 0
kount_words_with_X = 0
kount_words_with_Y = 0
kount_words_with_Z = 0


do i=1,count_wordle
chk_A = 0
chk_B = 0
chk_C = 0
chk_D = 0
chk_E = 0
chk_F = 0
chk_G = 0
chk_H = 0
chk_I = 0
chk_J = 0
chk_K = 0
chk_L = 0
chk_M = 0
chk_N = 0
chk_O = 0
chk_P = 0
chk_Q = 0
chk_R = 0
chk_S = 0
chk_T = 0
chk_U = 0
chk_V = 0
chk_W = 0
chk_X = 0
chk_Y = 0
chk_Z = 0
	if(POSSIBLE(i).eq.1) then
		kount_possible = kount_possible + 1
		write(*,*) (W(i,j), j=1,5)
		do j=1,5
			if(W(i,j).eq.'A') then
				if(chk_A.eq.0) then
					kount_words_with_A = kount_words_with_A + 1
					chk_A = 1
					go to 125
				else
					go to 125
				endif
			elseif(W(i,j).eq.'B') then
				if(chk_B.eq.0) then
					kount_words_with_B = kount_words_with_B + 1
					chk_B = 1
					go to 125
				else
					go to 125
				endif
			elseif(W(i,j).eq.'C') then
				if(chk_C.eq.0) then
					kount_words_with_C = kount_words_with_C + 1
					chk_C = 1
					go to 125
				else
					go to 125
				endif
			elseif(W(i,j).eq.'D') then
				if(chk_D.eq.0) then
					kount_words_with_D = kount_words_with_D + 1
					chk_D = 1
					go to 125
				else
					go to 125
				endif
			elseif(W(i,j).eq.'E') then
				if(chk_E.eq.0) then
					kount_words_with_E = kount_words_with_E + 1
					chk_E = 1
					go to 125
				else
					go to 125
				endif
			elseif(W(i,j).eq.'F') then
				if(chk_F.eq.0) then
					kount_words_with_F = kount_words_with_F + 1
					chk_F = 1
					go to 125
				else
					go to 125
				endif
			elseif(W(i,j).eq.'G') then
				if(chk_G.eq.0) then
					kount_words_with_G = kount_words_with_G + 1
					chk_G = 1
					go to 125
				else
					go to 125
				endif
			elseif(W(i,j).eq.'H') then
				if(chk_H.eq.0) then
					kount_words_with_H = kount_words_with_H + 1
					chk_H = 1
					go to 125
				else
					go to 125
				endif
			elseif(W(i,j).eq.'I') then
				if(chk_I.eq.0) then
					kount_words_with_I = kount_words_with_I + 1
					chk_I = 1
					go to 125
				else
					go to 125
				endif
			elseif(W(i,j).eq.'J') then
				if(chk_J.eq.0) then
					kount_words_with_J = kount_words_with_J + 1
					chk_J = 1
					go to 125
				else
					go to 125
				endif
			elseif(W(i,j).eq.'K') then
				if(chk_K.eq.0) then
					kount_words_with_K = kount_words_with_K + 1
					chk_K = 1
					go to 125
				else
					go to 125
				endif
			elseif(W(i,j).eq.'L') then
				if(chk_L.eq.0) then
					kount_words_with_L = kount_words_with_L + 1
					chk_L = 1
					go to 125
				else
					go to 125
				endif
			elseif(W(i,j).eq.'M') then
				if(chk_M.eq.0) then
					kount_words_with_M = kount_words_with_M + 1
					chk_M = 1
					go to 125
				else
					go to 125
				endif
			elseif(W(i,j).eq.'N') then
				if(chk_N.eq.0) then
					kount_words_with_N = kount_words_with_N + 1
					chk_N = 1
					go to 125
				else
					go to 125
				endif
			elseif(W(i,j).eq.'O') then
				if(chk_O.eq.0) then
					kount_words_with_O = kount_words_with_O + 1
					chk_O = 1
					go to 125
				else
					go to 125
				endif
			elseif(W(i,j).eq.'P') then
				if(chk_P.eq.0) then
					kount_words_with_P = kount_words_with_P + 1
					chk_P = 1
					go to 125
				else
					go to 125
				endif
			elseif(W(i,j).eq.'Q') then
				if(chk_Q.eq.0) then
					kount_words_with_Q = kount_words_with_Q + 1
					chk_Q = 1
					go to 125
				else
					go to 125
				endif
			elseif(W(i,j).eq.'R') then
				if(chk_R.eq.0) then
					kount_words_with_R = kount_words_with_R + 1
					chk_R = 1
					go to 125
				else
					go to 125
				endif
			elseif(W(i,j).eq.'S') then
				if(chk_S.eq.0) then
					kount_words_with_S = kount_words_with_S + 1
					chk_S = 1
					go to 125
				else
					go to 125
				endif
			elseif(W(i,j).eq.'T') then
				if(chk_T.eq.0) then
					kount_words_with_T = kount_words_with_T + 1
					chk_T = 1
					go to 125
				else
					go to 125
				endif
			elseif(W(i,j).eq.'U') then
				if(chk_U.eq.0) then
					kount_words_with_U = kount_words_with_U + 1
					chk_U = 1
					go to 125
				else
					go to 125
				endif
			elseif(W(i,j).eq.'V') then
				if(chk_V.eq.0) then
					kount_words_with_V = kount_words_with_V + 1
					chk_V = 1
					go to 125
				else
					go to 125
				endif
			elseif(W(i,j).eq.'W') then
				if(chk_W.eq.0) then
					kount_words_with_W = kount_words_with_W + 1
					chk_W = 1
					go to 125
				else
					go to 125
				endif
			elseif(W(i,j).eq.'X') then
				if(chk_X.eq.0) then
					kount_words_with_X = kount_words_with_X + 1
					chk_X = 1
					go to 125
				else
					go to 125
				endif
			elseif(W(i,j).eq.'Y') then
				if(chk_Y.eq.0) then
					kount_words_with_Y = kount_words_with_Y + 1
					chk_Y = 1
					go to 125
				else
					go to 125
				endif
			elseif(W(i,j).eq.'Z') then
				if(chk_Z.eq.0) then
					kount_words_with_Z = kount_words_with_Z + 1
					chk_Z = 1
					go to 125
				else
					go to 125
				endif
			endif
			125 continue
		enddo

!		write(9,*) (W(i,j), j=1,5)
	endif
enddo

write(*,*) ' number of possible words = ', kount_possible

write(*,*) ' '
write(*,*) ' Step 1 of the evaluation phase:'
write(*,*) ' '
write(*,*) ' Do you want the program to provide a list of how many words have each alphabet letter?'
write(*,*) ' (if a letter does not appear in the list, that means there are zero words with that letter)'
write(*,*) ' Enter 1 for Yes'
write(*,*) ' Enter 0 for No'
read(*,*) idec
if(idec.eq.1) then
	if(kount_words_with_A.ne.0) write(*,*) 'number of words with A = ',kount_words_with_A
	if(kount_words_with_B.ne.0) write(*,*) 'number of words with B = ',kount_words_with_B
	if(kount_words_with_C.ne.0) write(*,*) 'number of words with C = ',kount_words_with_C
	if(kount_words_with_D.ne.0) write(*,*) 'number of words with D = ',kount_words_with_D
	if(kount_words_with_E.ne.0) write(*,*) 'number of words with E = ',kount_words_with_E
	if(kount_words_with_F.ne.0) write(*,*) 'number of words with F = ',kount_words_with_F
	if(kount_words_with_G.ne.0) write(*,*) 'number of words with G = ',kount_words_with_G
	if(kount_words_with_H.ne.0) write(*,*) 'number of words with H = ',kount_words_with_H
	if(kount_words_with_I.ne.0) write(*,*) 'number of words with I = ',kount_words_with_I
	if(kount_words_with_J.ne.0) write(*,*) 'number of words with J = ',kount_words_with_J
	if(kount_words_with_K.ne.0) write(*,*) 'number of words with K = ',kount_words_with_K
	if(kount_words_with_L.ne.0) write(*,*) 'number of words with L = ',kount_words_with_L
	if(kount_words_with_M.ne.0) write(*,*) 'number of words with M = ',kount_words_with_M
	if(kount_words_with_N.ne.0) write(*,*) 'number of words with N = ',kount_words_with_N
	if(kount_words_with_O.ne.0) write(*,*) 'number of words with O = ',kount_words_with_O
	if(kount_words_with_P.ne.0) write(*,*) 'number of words with P = ',kount_words_with_P
	if(kount_words_with_Q.ne.0) write(*,*) 'number of words with Q = ',kount_words_with_Q
	if(kount_words_with_R.ne.0) write(*,*) 'number of words with R = ',kount_words_with_R
	if(kount_words_with_S.ne.0) write(*,*) 'number of words with S = ',kount_words_with_S
	if(kount_words_with_T.ne.0) write(*,*) 'number of words with T = ',kount_words_with_T
	if(kount_words_with_U.ne.0) write(*,*) 'number of words with U = ',kount_words_with_U
	if(kount_words_with_V.ne.0) write(*,*) 'number of words with V = ',kount_words_with_V
	if(kount_words_with_W.ne.0) write(*,*) 'number of words with W = ',kount_words_with_W
	if(kount_words_with_X.ne.0) write(*,*) 'number of words with X = ',kount_words_with_X
	if(kount_words_with_Y.ne.0) write(*,*) 'number of words with Y = ',kount_words_with_Y
	if(kount_words_with_Z.ne.0) write(*,*) 'number of words with Z = ',kount_words_with_Z
endif

idec_step2 = 0
idec_step3 = 0

write(*,*) ' '
write(*,*) ' Step 2 of the evaluation phase:'
write(*,*) ' '
write(*,*) ' Do you want the program to report summary statistics for an evaluation '
write(*,*) ' of all possible 5-letter words against all the possible wordle words?'
write(*,*) ' '
write(*,*) '      It will report the Top 10 words according to each of four criteria:'
write(*,*) '      (1) max group size,'
write(*,*) '      (2) mean grp size,'
write(*,*) '      (3) no. of size-1 grps, and '
write(*,*) '      (4) no. of 1- & 2-sized grps'
write(*,*) ' '
write(*,*) ' Enter 1 for Yes'
write(*,*) ' Enter 0 for No'
read(*,*) idec_step2

if(idec_step2.eq.1) then
	counter_all = 0
	goto 165
endif

345 continue
write(*,*) ' '
write(*,*) ' Step 3 of the evaluation phase:'
write(*,*) ' '
write(*,*) ' Do you want to propose a word to get a detailed evaluation against all the possible wordle words.'
write(*,*) ' Enter 1 for Yes'
write(*,*) ' Enter 0 for No'
read(*,*) idec_step3
if(idec_step3.eq.0) goto 245

165 continue
!start the loop on evaluating user-proposed words
!first check if it is a single-word evaluation or a dictionary evaluation

if(idec_step3.eq.1) then
	write(*,*) ' Starting in column 1, enter the word you want to evaluate against all the possible words'
	write(*,*) ' (capitalization is not important)'
	read(*,21) (pretend_prop_word(k), k=1,5)
elseif(idec_step2.eq.1) then
	counter_all = counter_all + 1
!initialize Top 10 placeholders
	if(counter_all.eq.1) then
		do k=1,10
			do k2=1,5
				prop_word_max_t10(k,k2) = '*'
				prop_word_mean_t10(k,k2) = '*'
				prop_word_ones_t10(k,k2) = '*'
				prop_word_ones_twos_t10(k,k2) = '*'
			enddo

			max_t10(k) = 15000
				max_t10_mean(k) = 99999
				max_t10_ones(k) = -99999
				max_t10_ones_twos(k) = -99999
			mean_t10(k) = 15000.0
				mean_t10_max(k) = 99999
				mean_t10_ones(k) = -99999
				mean_t10_ones_twos(k) = -99999
			ones_t10(k) = 0
				ones_t10_max(k) = 99999
				ones_t10_mean(k) = 99999
				ones_t10_ones_twos(k) = -99999
			ones_twos_t10(k) = 0
				ones_twos_t10_max(k) = 99999
				ones_twos_t10_mean(k) = 99999
				ones_twos_t10_ones(k) = -99999
		enddo
	endif

	do k=1,5
		pretend_prop_word(k) = ALL(counter_all,k)
	enddo

endif

do i=1,count_wordle
	if(POSSIBLE(i).eq.1) then
!this is the tough part. figuring out the wordle output
		do k=1,5
			position_check_1(k)=0
			position_check_2(k)=0
			output(i,k) = '*'
		enddo

		do j=1,5
			call cap_check(pretend_prop_word(j))
		enddo

!first check to see if any letters are correct and in the right place

		do j=1,5
			if(pretend_prop_word(j).eq.W(i,j)) then
!right letter and in the right place
				call cap_check(pretend_prop_word(j))
				output(i,j) = pretend_prop_word(j)
!keep track of which positions in W(i,j) have been matched to a position in proposed_word()
				position_check_1(j) = 1
			endif
		enddo

		do k=1,5
			if(position_check_1(k).eq.1) go to 175
			do j=1,5
!if jth position in W(i,j) already perfectly matches the same position in proposed_word(), skip this value of j
				if(position_check_1(j).eq.1) go to 155
!if jth position in W(i,j) has already been matched in Loop 2, skip this value of j
				if(position_check_2(j).eq.1) go to 155
				if(pretend_prop_word(k).eq.W(i,j)) then
!right letter wrong place
					call lower_case_check(pretend_prop_word(k))
					output(i,k) = pretend_prop_word(k)
					position_check_2(j) = 1
					go to 175
				endif
				155 continue
			enddo
			175 continue
		enddo
	endif
enddo

if(idec_step3.eq.1) then
!now print out the evaluations for the POSSIBLE(i) words

	write(*,*) 'For the wordle output below, '
	write(*,*) '  an asterisk (*) corresponds to a letter with no match'
	write(*,*) '  a lower case letter corresponds to a matching letter that is in the wrong position'
	write(*,*) '  and a capital letter corresponds to a matching letter that is in the right position'
	write(*,*) ' '
endif

31 format(' When the wordle word = possible word ',5a1,', the wordle output for the proposed word = ',5a1)

do i=1,count_wordle
	istar(i) = 0
enddo

kount_possible = 0
grp_number = 0

do i=1,20000
	grp_count(i) = 0
enddo

do i=1,count_wordle
	if(POSSIBLE(i).eq.0) goto 195
	kount_possible = kount_possible + 1

	if(istar(i).eq.0) then
		if(idec_step3.eq.1) then
			write(*,31) (W(i,j), j=1,5), (output(i,j), j=1,5)
		endif

		grp_number = grp_number + 1
		grp_count(grp_number) = grp_count(grp_number) + 1
		if(i.eq.count_wordle) goto 205
	else
		goto 195
	endif

	do ichk=i+1,count_wordle
		if(POSSIBLE(ichk).eq.0) goto 215
		do j=1,5
			if(output(i,j).ne.output(ichk,j)) then
				goto 215
			endif
		enddo

		if(idec_step3.eq.1) then
			write(*,31) (W(ichk,j), j=1,5), (output(ichk,j), j=1,5)
		endif

		grp_count(grp_number) = grp_count(grp_number) + 1
		istar(ichk)=1
215 		continue
	enddo
195 	continue

enddo
205 continue

do i=1,20
	kount(i)=0
enddo

!kount(i) is the number of groups that have size i, up to size 19.
!all the groups of size 20 or more are lumped together in kount(20).

!real_kount(i) is the number of groups that have size i, where i can
! go up to 15,000.  Since there are currently only a max of about 2400
! wordle words, this should work to give me all the counts.

do i=1,15000
	real_kount(i)=0
enddo

!grp_number is the total number of groups.
!each group has a unique i.d. number that ranges from 1 to the number of groups.
!grp_count(i) is the number of words in group i, that is, the size of group i.

max_size = 0
do i=1,grp_number
	if(grp_count(i).gt.max_size) max_size = grp_count(i)
	if(grp_count(i).gt.20) then
		kount(20) = kount(20) + 1
		goto 225
	endif
	do j=1,20
		if(grp_count(i).eq.j) then
			kount(j) = kount(j) + 1
			goto 225
		endif
	enddo
225 continue
	do k=1,20000
		if(grp_count(i).eq.k) then
			real_kount(k) = real_kount(k) + 1
			goto 235
		endif
	enddo
235 continue
enddo


!real_kount(i) is the number of groups that have size i
!one way to find the average group size for a randomly chosen word is as follow:
! mean_grp_size = [sum_over_i of (real_kount(i)*i*i)]/total number of words

sum_grp_size=0
do i=1,20000
	sum_grp_size = sum_grp_size + real_kount(i)*i*i
enddo

xkount_possible = kount_possible

xsum_grp_size = sum_grp_size
mean_grp_size = xsum_grp_size/xkount_possible


xgrp_number = grp_number
!mean_size is the average group size for a randomly chosen group.
mean_size = xkount_possible/xgrp_number

if(idec_step3.eq.1) then

	write(*,*) " Group Size Distribution:"
	DIST_LABEL1=' Group Size:     1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17  18  19 >=20'
	DIST_LABEL2=' No. of groups:'
	DIST_LABEL3=' No. of words: '

	write(*,*) DIST_LABEL1
	write(*,41) DIST_LABEL2, (kount(i), i=1,20)
41 format(a15,20(1x,i3))
	write(*,41) DIST_LABEL3, (i*kount(i), i=1,20)
	write(*,51) mean_size
51 format(' average group size for a randomly chosen group = ', f6.1)
	write(*,61) mean_grp_size
61 format(' average group size for a randomly chosen word  = ', f6.1)
	write(*,*) ' maximum group size = ', max_size
	write(*,*) ' total number of possible words = ', kount_possible
	write(*,*) ' total number of groups = ',grp_number
endif

ones = kount(1)
ones_twos = kount(1) + 2*kount(2)

if(idec_step2.eq.1) then

!here I need to keep track of all the Top 10 stuff

	do j=1,5
		call cap_check(pretend_prop_word(j))
	enddo

	do k=1,10

		if(max_size.le.max_t10(k)) then

			if(k.eq.10) goto 275

			do k2=10,k+1,-1
				max_t10(k2) = max_t10(k2-1)
				max_t10_mean(k2) = max_t10_mean(k2-1)
				max_t10_ones(k2) = max_t10_ones(k2-1)
				max_t10_ones_twos(k2) = max_t10_ones_twos(k2-1)
				do j=1,5
					prop_word_max_t10(k2,j) = prop_word_max_t10(k2-1,j)
				enddo

			enddo

275			continue

			max_t10(k) = max_size
			max_t10_mean(k) = mean_grp_size
			max_t10_ones(k) = ones
			max_t10_ones_twos(k) = ones_twos
			do j=1,5
				prop_word_max_t10(k,j) = pretend_prop_word(j)
			enddo
			goto 25
		endif
	enddo
25	continue

	do k=1,10

		if(mean_grp_size.le.mean_t10(k)) then

			if(k.eq.10) goto 285

			do k2=10,k+1,-1
				mean_t10(k2) = mean_t10(k2-1)
				mean_t10_max(k2) = mean_t10_max(k2-1)
				mean_t10_ones(k2) = mean_t10_ones(k2-1)
				mean_t10_ones_twos(k2) = mean_t10_ones_twos(k2-1)
				do j=1,5
					prop_word_mean_t10(k2,j) = prop_word_mean_t10(k2-1,j)
				enddo

			enddo

285			continue

			mean_t10(k) = mean_grp_size
			mean_t10_max(k) = max_size
			mean_t10_ones(k) = ones
			mean_t10_ones_twos(k) = ones_twos
			do j=1,5
				prop_word_mean_t10(k,j) = pretend_prop_word(j)
			enddo
			goto 85
		endif
	enddo
85	continue

	do k=1,10
		if(ones.ge.ones_t10(k)) then

			if(k.eq.10) goto 295

			do k2=10,k+1,-1
				ones_t10(k2) = ones_t10(k2-1)
				ones_t10_max(k2) = ones_t10_max(k2-1)
				ones_t10_mean(k2) = ones_t10_mean(k2-1)
				ones_t10_ones_twos(k2) = ones_t10_ones_twos(k2-1)
				do j=1,5
					prop_word_ones_t10(k2,j) = prop_word_ones_t10(k2-1,j)
				enddo
			enddo

295			continue

			ones_t10(k) = ones
			ones_t10_max(k) = max_size
			ones_t10_mean(k) = mean_grp_size
			ones_t10_ones_twos(k) = ones_twos
			do j=1,5
				prop_word_ones_t10(k,j) = pretend_prop_word(j)
			enddo
			goto 255
		endif
	enddo
255	continue

	do k=1,10
		if(ones_twos.ge.ones_twos_t10(k)) then

			if(k.eq.10) goto 305

			do k2=10,k+1,-1
				ones_twos_t10(k2) = ones_twos_t10(k2-1)
				ones_twos_t10_max(k2) = ones_twos_t10_max(k2-1)
				ones_twos_t10_mean(k2) = ones_twos_t10_mean(k2-1)
				ones_twos_t10_ones(k2) = ones_twos_t10_ones(k2-1)
				do j=1,5
					prop_word_ones_twos_t10(k2,j) = prop_word_ones_twos_t10(k2-1,j)
				enddo

			enddo

305			continue

			ones_twos_t10(k) = ones_twos
			ones_twos_t10_max(k) = max_size
			ones_twos_t10_mean(k) = mean_grp_size
			ones_twos_t10_ones(k) = ones
			do j=1,5
				prop_word_ones_twos_t10(k,j) = pretend_prop_word(j)
			enddo
			goto 265
		endif
	enddo

265 	continue

! at this point I have updated the top 10 stuff.
! now, if I am not done with all the dictionary words, I need to loop back up to the top.

	if(counter_all.lt.count_all) goto 165

!if counter_all is equal to count_all, then we want to print out our results and find out
!what the user wants to do next.
	Crit1 = '    Max   '
	Crit2 = '   Mean   '
	Crit3 = ' # of 1s  '
	Crit4 = '# of 1+2s '
	OUT_LABELS1='            Proposed  Max grp   Mean grp  no. of   no. of  '
	OUT_LABELS2=' Criterion    Word    size       size      1s      1s + 2s '
	OUT_LABELS3=' ---------   -----    ----      ------   ------   ---------'
	OUT_LABELS4='-----------------------------------------------------------'

	write(*,71) OUT_LABELS1
	write(*,71) OUT_LABELS2
	write(*,71) OUT_LABELS3
71 format(1x,a60)

81 format(1x,a10,3x,5a1,4x,i4,6x,f6.1,4x,i4,6x,i4)

	do k=1,10
		write(*,81) Crit1, (prop_word_max_t10(k,j), j=1,5), max_t10(k), max_t10_mean(k), max_t10_ones(k), max_t10_ones_twos(k)
	enddo

	write(*,71) OUT_LABELS4

	do k=1,10
		write(*,81) Crit2, (prop_word_mean_t10(k,j), j=1,5), mean_t10_max(k), mean_t10(k), mean_t10_ones(k), mean_t10_ones_twos(k)
	enddo

	write(*,71) OUT_LABELS4

	do k=1,10
		write(*,81) Crit3, (prop_word_ones_t10(k,j), j=1,5), ones_t10_max(k), ones_t10_mean(k), ones_t10(k), ones_t10_ones_twos(k)
	enddo

	write(*,71) OUT_LABELS4

	do k=1,10
		write(*,81) Crit4, (prop_word_ones_twos_t10(k,j), j=1,5), ones_twos_t10_max(k), ones_twos_t10_mean(k), ones_twos_t10_ones(k), &
		ones_twos_t10(k)
	enddo

endif

!end of Step 2 of the evaluation phase
!now I need to set idec_step2=0 and loop back up to the decision for idec_step3
if(idec_step2.eq.1) then
	idec_step2=0
	goto 345
elseif(idec_step3.eq.1) then
	write(*,*) ' '
	write(*,*) ' Do you want to evaluate another proposed word?'
	write(*,*) ' Enter 1 for Yes'
	write(*,*) ' Enter 0 for No'
	read(*,*) idec_step3
	if(idec_step3.eq.1) then
		go to 165
	else
		go to 245
	endif
endif

245 continue
write(*,*) ' '
write(*,*) ' Do you want to enter the wordle feedback for another try?'
write(*,*) ' Enter 1 for Yes'
write(*,*) ' Enter 0 for No'
read(*,*) idec
if(idec.eq.1) go to 15

write(*,*) ' '
write(*,*) ' Do you want to update the list of the used wordle words with the winning word?'
write(*,*) ' Enter 1 for Yes'
write(*,*) ' Enter 0 for No'
read(*,*) idec

if(idec.eq.1) then
	write(*,*) ' '
	write(*,*) ' Enter the winning wordle word (starting in column 1 on your screen):'
	read(*,21) (winning_word(j), j=1,5)
21      format(5a1)
	do j=1,5
		call cap_check(winning_word(j))
	enddo

	open(unit=1,file='wordle_list_used.txt')
	do k=1,count_wordle_used
		write(1,21) (USED(k,j), j=1,5)
	enddo
	write(1,21) (winning_word(j), j=1,5)
	CLOSE(1)
endif
end

subroutine cap_check(cjunk)
character*1 cjunk
		if(cjunk.eq.'a') cjunk='A'
		if(cjunk.eq.'b') cjunk='B'
		if(cjunk.eq.'c') cjunk='C'
		if(cjunk.eq.'d') cjunk='D'
		if(cjunk.eq.'e') cjunk='E'
		if(cjunk.eq.'f') cjunk='F'
		if(cjunk.eq.'g') cjunk='G'
		if(cjunk.eq.'h') cjunk='H'
		if(cjunk.eq.'i') cjunk='I'
		if(cjunk.eq.'j') cjunk='J'
		if(cjunk.eq.'k') cjunk='K'
		if(cjunk.eq.'l') cjunk='L'
		if(cjunk.eq.'m') cjunk='M'
		if(cjunk.eq.'n') cjunk='N'
		if(cjunk.eq.'o') cjunk='O'
		if(cjunk.eq.'p') cjunk='P'
		if(cjunk.eq.'q') cjunk='Q'
		if(cjunk.eq.'r') cjunk='R'
		if(cjunk.eq.'s') cjunk='S'
		if(cjunk.eq.'t') cjunk='T'
		if(cjunk.eq.'u') cjunk='U'
		if(cjunk.eq.'v') cjunk='V'
		if(cjunk.eq.'w') cjunk='W'
		if(cjunk.eq.'x') cjunk='X'
		if(cjunk.eq.'y') cjunk='Y'
		if(cjunk.eq.'z') cjunk='Z'
return
end
subroutine lower_case_check(cjunk)
character*1 cjunk
		if(cjunk.eq.'A') cjunk='a'
		if(cjunk.eq.'B') cjunk='b'
		if(cjunk.eq.'C') cjunk='c'
		if(cjunk.eq.'D') cjunk='d'
		if(cjunk.eq.'E') cjunk='e'
		if(cjunk.eq.'F') cjunk='f'
		if(cjunk.eq.'G') cjunk='g'
		if(cjunk.eq.'H') cjunk='h'
		if(cjunk.eq.'I') cjunk='i'
		if(cjunk.eq.'J') cjunk='j'
		if(cjunk.eq.'K') cjunk='k'
		if(cjunk.eq.'L') cjunk='l'
		if(cjunk.eq.'M') cjunk='m'
		if(cjunk.eq.'N') cjunk='n'
		if(cjunk.eq.'O') cjunk='o'
		if(cjunk.eq.'P') cjunk='p'
		if(cjunk.eq.'Q') cjunk='q'
		if(cjunk.eq.'R') cjunk='r'
		if(cjunk.eq.'S') cjunk='s'
		if(cjunk.eq.'T') cjunk='t'
		if(cjunk.eq.'U') cjunk='u'
		if(cjunk.eq.'V') cjunk='v'
		if(cjunk.eq.'W') cjunk='w'
		if(cjunk.eq.'X') cjunk='x'
		if(cjunk.eq.'Y') cjunk='y'
		if(cjunk.eq.'Z') cjunk='z'
return
end
