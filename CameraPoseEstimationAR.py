import numpy as np
import cv2 as cv

# video 불러오기
video_file = r"C:\CV\data_Chess\chessboard_sample.mp4"

# calibration 결과 불러오기(.npz)
data = np.load(r"C:\CV\data_Chess\calibration_result.npz")
K = data["K"]
dist_coeff = data["dist"]

# 체스보드 설정
board_pattern = (10, 7)
board_cellsize = 0.025
board_criteria = cv.CALIB_CB_ADAPTIVE_THRESH + cv.CALIB_CB_NORMALIZE_IMAGE + cv.CALIB_CB_FAST_CHECK

# video 열기
video = cv.VideoCapture(video_file)
assert video.isOpened(), 'Cannot read the given input, ' + video_file

# 체스보드 평면 위의 3D 좌표 설정
obj_points = board_cellsize * np.array([[c, r, 0] for r in range(board_pattern[1]) for c in range(board_pattern[0])])

# 체스보드 (5,3) 좌표의 z = -1.5 위에 위치
text_3d = np.array([[5, 3, -1.5]], dtype=np.float32) * board_cellsize

"""
# XYZ 좌표계 (원점)
axis_length = 0.1
axis_3d = np.float32([
    [0, 0, 0],
    [axis_length, 0, 0],
    [0, axis_length, 0],
    [0, 0, -axis_length],
])
"""

# 영상 재생
while True:
    valid, img = video.read()
    if not valid:
        break
    
    # Camera Pose Estimation
    success, img_points = cv.findChessboardCorners(img, board_pattern, board_criteria)
    if success:
        ret, rvec, tvec = cv.solvePnP(obj_points, img_points, K, dist_coeff)
        
        # Chess 텍스트 표시
        text_chess, _ = cv.projectPoints(text_3d, rvec, tvec, K, dist_coeff)
        pt = tuple(np.int32(text_chess[0].ravel()))
        cv.putText(img, "Chess", pt, cv.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2)
        
        """ 
        # XYZ축 표시
        axis_xyz, _ = cv.projectPoints(axis_3d, rvec, tvec, K, dist_coeff)
        corner = tuple(axis_xyz[0].ravel().astype(int))
        x_axis = tuple(axis_xyz[1].ravel().astype(int))
        y_axis = tuple(axis_xyz[2].ravel().astype(int))
        z_axis = tuple(axis_xyz[3].ravel().astype(int))

        cv.line(img, corner, x_axis, (0, 0, 255), 3)
        cv.line(img, corner, y_axis, (0, 255, 0), 3)
        cv.line(img, corner, z_axis, (255, 0, 0), 3)
        """
        
        # 카메라 위치 추정
        R, _ = cv.Rodrigues(rvec)
        p = (-R.T @ tvec).flatten()
        info = f'XYZ: [{p[0]:.3f} {p[1]:.3f} {p[2]:.3f}]'
        cv.putText(img, info, (10, 25), cv.FONT_HERSHEY_DUPLEX, 0.6, (0, 255, 0))
    
    # 시각화
    cv.imshow('Pose Estimation (Chessboard)', img)
    
    # 키 설정
    key = cv.waitKey(10)
    if key == ord(' '):  # Space : 정지
        key = cv.waitKey()
    if key == 27:  # ESC : 종료
        break

# 종료 시 리소스 해제
video.release()
cv.destroyAllWindows()