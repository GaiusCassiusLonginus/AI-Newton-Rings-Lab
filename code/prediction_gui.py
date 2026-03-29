import sys
import numpy as np
import pandas as pd
import torch
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QFileDialog,
    QComboBox, QMessageBox, QTextEdit, QHBoxLayout, QSplitter, QVBoxLayout
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from src.model import *  # 请确保导入你实现的模型文件
import matplotlib
import sys
import os
if getattr(sys, 'frozen', False):
    # 如果是打包后的可执行文件
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))
# 将应用路径添加到系统路径
sys.path.insert(0, os.path.join(application_path, 'src'))
matplotlib.use('Agg')  # 使用非交互式后端，避免与Qt冲突
class ModelGUI(QWidget):
    def __init__(self):
        super().__init__()
        # 初始化默认值
        self.train_dataset_path = None
        self.test_dataset_path = None
        self.model = None
        self.m_in = None  # 用于输入数据的归一化
        self.m_out = None  # 用于输出数据的归一化
        self.error_threshold = None  # 误差阈值
        self.initUI()
    def initUI(self):
        self.setWindowTitle("预测分析系统")
        self.setGeometry(100, 100, 1000, 700)
        # 主布局
        main_layout = QVBoxLayout()
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        # 左侧控制面板
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)
        # 右侧结果显示区域
        self.result_widget = QTextEdit()
        self.result_widget.setReadOnly(True)
        # 添加一个用于显示图像的标签
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(400, 300)
        # 右侧布局
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.result_widget)
        right_layout.addWidget(self.image_label)
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        splitter.addWidget(control_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 700])
        # 控制面板内容
        self.model_label = QLabel("选择模型:")
        control_layout.addWidget(self.model_label)
        self.model_selector = QComboBox()
        self.model_selector.addItems([
            "LSTM", "Transformer_KAN"
        ])
        control_layout.addWidget(self.model_selector)
        self.epoch_label = QLabel("设置训练次数:")
        control_layout.addWidget(self.epoch_label)
        self.epoch_input = QLineEdit("500")
        control_layout.addWidget(self.epoch_input)
        self.lr_label = QLabel("训练学习速度:")
        control_layout.addWidget(self.lr_label)
        self.lr_input = QLineEdit("0.0005")
        control_layout.addWidget(self.lr_input)
        # 误差阈值设置
        self.threshold_layout = QHBoxLayout()
        self.threshold_label = QLabel("误差阈值:")
        self.threshold_layout.addWidget(self.threshold_label)
        self.threshold_input = QLineEdit("0.1")
        self.threshold_layout.addWidget(self.threshold_input)
        control_layout.addLayout(self.threshold_layout)
        self.data_label = QLabel("选择训练数据文件:")
        control_layout.addWidget(self.data_label)
        self.data_button = QPushButton("引入")
        self.data_button.clicked.connect(self.load_dataset)
        control_layout.addWidget(self.data_button)
        self.test_label = QLabel("选择测试数据文件:")
        control_layout.addWidget(self.test_label)
        self.test_button = QPushButton("引入")
        self.test_button.clicked.connect(self.load_test_dataset)
        control_layout.addWidget(self.test_button)
        self.run_button = QPushButton("训练并且保存模型")
        self.run_button.clicked.connect(self.train_and_save_model)
        control_layout.addWidget(self.run_button)
        self.load_button = QPushButton("引入训练模型")
        self.load_button.clicked.connect(self.load_model)
        control_layout.addWidget(self.load_button)
        self.predict_button = QPushButton("开始测试")
        self.predict_button.clicked.connect(self.test_model)
        control_layout.addWidget(self.predict_button)
        # 不确定度置信水平设置
        self.confidence_layout = QHBoxLayout()
        self.confidence_label = QLabel("置信水平 (%):")
        self.confidence_layout.addWidget(self.confidence_label)
        self.confidence_input = QComboBox()
        self.confidence_input.addItems(["90", "95", "99"])
        self.confidence_input.setCurrentIndex(1)  # 默认95%
        self.confidence_layout.addWidget(self.confidence_input)
        control_layout.addLayout(self.confidence_layout)
        # 添加分割器到主布局
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
    def load_dataset(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择训练数据文件", "", "CSV Files (*.csv);;All Files (*)")
        if file_path:
            self.train_dataset_path = file_path  # 设置训练数据路径
            self.append_result(f"训练数据集已加载: {file_path}")
    def load_test_dataset(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择测试数据文件", "", "CSV Files (*.csv);;All Files (*)")
        if file_path:
            self.test_dataset_path = file_path  # 设置测试数据路径
            self.append_result(f"测试数据集已加载: {file_path}")
    def append_result(self, message):
        """在结果区域添加消息"""
        self.result_widget.append(message)
        self.result_widget.append("-" * 50)
    def train_and_save_model(self):
        try:
            if not self.train_dataset_path:
                raise ValueError("请先加载训练数据集")  # 检查是否加载了训练数据
            # Load training data
            dataset = pd.read_csv(self.train_dataset_path)
            values = dataset.values[:, 1:]
            values = np.array(values)
            num_samples = values.shape[0]
            n_out = 1
            # Split into training and testing sets
            per = np.random.permutation(num_samples)
            n_train_number = per[:int(num_samples * 0.8)]
            n_val_number = per[int(num_samples * 0.8):]  # 添加验证集
            Xtrain = values[n_train_number, :values.shape[1] - n_out]
            Ytrain = values[n_train_number, values.shape[1] - n_out:]
            Ytrain = Ytrain.reshape(-1, n_out)
            # 添加验证集
            Xval = values[n_val_number, :values.shape[1] - n_out]
            Yval = values[n_val_number, values.shape[1] - n_out:]
            Yval = Yval.reshape(-1, n_out)
            # Normalize data
            self.m_in = MinMaxScaler()
            vp_train = self.m_in.fit_transform(Xtrain)
            vp_val = self.m_in.transform(Xval)  # 使用相同的scaler转换验证集
            self.m_out = MinMaxScaler()
            vt_train = self.m_out.fit_transform(Ytrain)
            vt_val = self.m_out.transform(Yval)  # 使用相同的scaler转换验证集
            vp_train = vp_train.reshape((vp_train.shape[0], 1, vp_train.shape[1]))
            vp_val = vp_val.reshape((vp_val.shape[0], 1, vp_val.shape[1]))
            # Convert to tensors
            X_TRAIN = torch.from_numpy(vp_train).type(torch.Tensor)
            Y_TRAIN = torch.from_numpy(vt_train).type(torch.Tensor)
            X_VAL = torch.from_numpy(vp_val).type(torch.Tensor)
            Y_VAL = torch.from_numpy(vt_val).type(torch.Tensor)
            # Model setup
            model_name = self.model_selector.currentText()
            input_dim = vp_train.shape[2]
            output_dim = n_out
            hidden_dim = 100
            num_layers = 2
            if model_name == 'LSTM':
                self.model = LSTM(input_dim=input_dim, hidden_dim=hidden_dim, num_layers=num_layers,
                                  output_dim=output_dim)
            elif model_name == 'Transformer_KAN':
                self.model = TimeSeriesTransformer_ekan(input_dim=input_dim, num_heads=8, num_layers=num_layers,
                                                        num_outputs=output_dim, hidden_space=32, dropout_rate=0.2)
            else:
                raise ValueError("模型未实现")
            # Training
            epochs = int(self.epoch_input.text())
            lr = float(self.lr_input.text())
            criterion = torch.nn.MSELoss()
            optimiser = torch.optim.Adam(self.model.parameters(), lr=lr)
            self.append_result(f"开始训练模型: {model_name}")
            self.append_result(f"训练参数: 轮次={epochs}, 学习率={lr}")
            # 初始化列表来记录训练和验证损失
            train_losses = []
            val_losses = []
            for t in range(epochs):
                # 训练阶段
                self.model.train()
                y_train_pred = self.model(X_TRAIN)
                loss = criterion(y_train_pred, Y_TRAIN)
                optimiser.zero_grad()
                loss.backward()
                optimiser.step()
                # 验证阶段
                self.model.eval()
                with torch.no_grad():
                    y_val_pred = self.model(X_VAL)
                    val_loss = criterion(y_val_pred, Y_VAL)
                # 记录损失
                train_losses.append(loss.item())
                val_losses.append(val_loss.item())
                if t % 100 == 0 or t == epochs - 1:
                    self.append_result(f"轮次 {t + 1}/{epochs}, 训练损失: {loss.item():.6f}, 验证损失: {val_loss.item():.6f}")
            self.append_result(f"训练完成! 最终训练损失: {loss.item():.6f}, 最终验证损失: {val_loss.item():.6f}")
            # 绘制训练曲线
            self.plot_training_curve(train_losses, val_losses, epochs)
            # Save model
            save_path, _ = QFileDialog.getSaveFileName(self, "保存模型", "", "PyTorch Model Files (*.pth)")
            if save_path:
                torch.save({
                    'model_state_dict': self.model.state_dict(),
                    'input_scaler': self.m_in,
                    'output_scaler': self.m_out
                }, save_path)
                self.append_result(f"模型已保存至: {save_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))
            self.append_result(f"错误: {str(e)}")
    def plot_training_curve(self, train_losses, val_losses, epochs):
        """绘制训练曲线"""
        plt.figure(figsize=(10, 6))
        plt.plot(range(1, epochs + 1), train_losses, label='训练损失')
        plt.plot(range(1, epochs + 1), val_losses, label='验证损失')
        plt.title('模型训练曲线')
        plt.xlabel('训练轮次')
        plt.ylabel('损失值')
        plt.legend()
        plt.grid(True)
        # 保存图像到临时文件
        plt.savefig('training_curve.png', bbox_inches='tight')
        plt.close()
        # 在GUI中显示图像
        pixmap = QPixmap('training_curve.png')
        self.image_label.setPixmap(pixmap.scaled(self.image_label.width(),
                                                 self.image_label.height(),
                                                 Qt.KeepAspectRatio))
        self.append_result("训练曲线已生成并显示")
    def load_model(self):
        try:
            load_path, _ = QFileDialog.getOpenFileName(self, "加载模型", "", "PyTorch Model Files (*.pth)")
            if load_path:
                checkpoint = torch.load(load_path, map_location=torch.device('cpu'),weights_only=False)
                model_name = self.model_selector.currentText()
                if model_name == 'LSTM':
                    self.model = LSTM(input_dim=checkpoint['input_scaler'].data_max_.shape[0],
                                      hidden_dim=100, num_layers=2, output_dim=1)
                elif model_name == 'Transformer_KAN':
                    self.model = TimeSeriesTransformer_ekan(input_dim=checkpoint['input_scaler'].data_max_.shape[0],
                                                            num_heads=8, num_layers=2, num_outputs=1,
                                                            hidden_space=32, dropout_rate=0.2)
                else:
                    raise ValueError("模型未实现")
                self.model.load_state_dict(checkpoint['model_state_dict'])
                self.m_in = checkpoint['input_scaler']
                self.m_out = checkpoint['output_scaler']
                self.model.eval()  # Switch to evaluation mode
                self.append_result(f"模型已加载: {load_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))
            self.append_result(f"错误: {str(e)}")
    def test_model(self):
        try:
            if not self.test_dataset_path:
                raise ValueError("请先加载测试数据集")  # 检查是否加载了测试数据
            if self.model is None or self.m_in is None or self.m_out is None:
                raise ValueError("请先加载或训练模型")
            # 使用用户设置的误差阈值
            self.error_threshold = float(self.threshold_input.text())
            self.append_result(f"使用用户设置的误差阈值: {self.error_threshold:.4f}")
            # Load test data
            test_dataset = pd.read_csv(self.test_dataset_path)
            values = test_dataset.values[:, 1:]
            n_out = 1
            values = np.array(values)
            Xtest = values[:, :values.shape[1] - n_out]
            Ytest = values[:, values.shape[1] - n_out:]
            Ytest = Ytest.reshape(-1, n_out)
            vp_test = self.m_in.transform(Xtest)
            vt_test = self.m_out.transform(Ytest)
            vp_test = vp_test.reshape((vp_test.shape[0], 1, vp_test.shape[1]))
            X_TEST = torch.from_numpy(vp_test).type(torch.Tensor)
            # Prediction
            self.append_result(f"开始预测测试数据...")
            self.model.eval()
            with torch.no_grad():
                y_test_pred = self.model(X_TEST)
            yhat = y_test_pred.detach().numpy()
            yhat = yhat.reshape(vp_test.shape[0], n_out)
            predicted_data = self.m_out.inverse_transform(yhat)
            # 计算预测误差
            errors = Ytest - predicted_data
            abs_errors = np.abs(errors)
            rmse = np.sqrt(mean_squared_error(Ytest, predicted_data))
            mae = np.mean(abs_errors)
            # 添加误差统计信息
            self.append_result(f"测试集误差统计:")
            self.append_result(f"最小误差: {np.min(abs_errors):.6f}")
            self.append_result(f"最大误差: {np.max(abs_errors):.6f}")
            self.append_result(f"平均误差: {mae:.6f}")
            self.append_result(f"误差标准差: {np.std(abs_errors):.6f}")
            # 检验输入数据正确性
            suspicious_indices = np.where(abs_errors > self.error_threshold)[0]
            num_suspicious = len(suspicious_indices)
            # 准备弹窗展示内容
            result_message = f"测试结果:\n\n"
            result_message += f"测试集RMSE: {rmse:.6f}\n"
            result_message += f"测试集MAE: {mae:.6f}\n"
            result_message += f"误差阈值: {self.error_threshold:.6f}\n"
            result_message += f"发现{num_suspicious}个可疑输入数据点\n\n"
            result_message += "前10个预测结果:\n"
            result_message += "样本 | 实际值 | 预测值 | 误差 | 状态\n"
            result_message += "-" * 50 + "\n"
            for i in range(min(10, len(predicted_data))):
                status = "正常" if abs_errors[i] <= self.error_threshold else "可疑"
                result_message += f"{i + 1:2} | {Ytest[i][0]:.6f} | {predicted_data[i][0]:.6f} | {errors[i][0]:.6f} | {status}\n"
            # 如果有可疑数据点，添加到结果中
            if num_suspicious > 0:
                result_message += f"\n可疑数据点索引: {suspicious_indices[:10]}"
                if num_suspicious > 10:
                    result_message += f" ... (共{num_suspicious}个)"
                # 创建误差分布图
                plt.figure(figsize=(10, 6))
                plt.plot(abs_errors, 'b-', label='预测误差')
                plt.axhline(y=self.error_threshold, color='r', linestyle='-', label='误差阈值')
                plt.scatter(suspicious_indices, abs_errors[suspicious_indices],
                            color='red', s=50, zorder=5, label='可疑数据点')
                plt.title('预测误差分布及可疑数据点')
                plt.xlabel('样本索引')
                plt.ylabel('绝对误差')
                plt.legend()
                plt.grid(True)
                # 保存图像到临时文件
                plt.savefig('error_plot.png', bbox_inches='tight')
                plt.close()
                # 在GUI中显示图像
                pixmap = QPixmap('error_plot.png')
                self.image_label.setPixmap(pixmap.scaled(self.image_label.width(),
                                                         self.image_label.height(),
                                                         Qt.KeepAspectRatio))
            # 在结果区域添加结果
            self.append_result(f"测试完成!\n{result_message}")
            # 弹窗展示结果
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("测试结果")
            msg_box.setText(result_message)
            if num_suspicious > 0:
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setInformativeText(f"发现{num_suspicious}个可疑输入数据点，请检查这些数据的正确性。")
            else:
                msg_box.setIcon(QMessageBox.Information)
                msg_box.setInformativeText("所有输入数据均正常。")
            msg_box.exec_()
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))
            self.append_result(f"错误: {str(e)}")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModelGUI()
    window.show()
    sys.exit(app.exec_())